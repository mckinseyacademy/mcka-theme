import tempfile
import urllib
import collections
import re
import uuid

from dateutil.parser import parse as parsedate

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.conf import settings

from accounts.middleware.thread_local import set_course_context, get_course_context
from admin.models import Program
from courses.models import FeatureFlags
from api_client.api_error import ApiError
from api_client import user_api, group_api, course_api, organization_api, project_api, user_models, workgroup_api
from accounts.models import UserActivation
from datetime import datetime
from pytz import UTC
from api_client.project_models import Project
from api_client.user_api import USER_ROLES

from license import controller as license_controller

from .models import (
    Client, WorkGroup, UserRegistrationError, BatchOperationErrors, WorkGroupActivityXBlock,
    GROUP_PROJECT_CATEGORY, GROUP_PROJECT_V2_CATEGORY,
    GROUP_PROJECT_V2_ACTIVITY_CATEGORY,
)

from lib.mail import sendMultipleEmails, email_add_active_student, email_add_inactive_student, email_add_single_new_user

from api_client.user_api import USER_ROLES
from .permissions import Permissions

import threading
import Queue
import atexit

import csv

# need to load everything up to first level nested XBlocks to properly get Group Project V2 activities
MINIMAL_COURSE_DEPTH = 5
# need to load one level more deep to get Group Project V2 stages as their close dates are needed for report
GROUP_WORK_REPORT_DEPTH = 6


class GroupProject(object):

    def _get_activity_link(self, course_id, activity_id):
        base_gw_url = reverse('user_course_group_work', kwargs={'course_id': course_id})
        query_string_key = 'activate_block_id' if self.is_v2 else 'seqid'
        return base_gw_url + "?" + urllib.urlencode({query_string_key: activity_id})

    def __init__(self, course_id, project_id, name, activities, vertical_id=None, is_v2=False):
        self.id = project_id
        self.course_id = course_id
        self.name = name
        self._activities = activities
        self.vertical_id = vertical_id
        self.is_v2 = is_v2

    @property
    def activities(self):
        for activity in self._activities:
            if not hasattr(activity, 'xblock'):
                activity.xblock = WorkGroupActivityXBlock.fetch_from_activity(self.course_id, activity.id)

            if self.is_v2:
                activity.due = activity.xblock.due_date

            activity.link = self._get_activity_link(self.course_id, activity.id)

        return self._activities


def _worker():
    while True:
        func, args, kwargs = _queue.get()
        try:
            func(*args, **kwargs)
        except:
            pass # bork or ignore here; ignore for now
        finally:
            _queue.task_done() # so we can join at exit

def postpone(func):
    def decorator(*args, **kwargs):
        _queue.put((func, args, kwargs))
    return decorator

def _cleanup():
    _queue.join() # so we don't exit too soon

_queue = Queue.Queue()
atexit.register(_cleanup)


def upload_student_list_threaded(student_list, client_id, absolute_uri, reg_status):
    _thread = threading.Thread(target = _worker) # one is enough; it's postponed after all
    _thread.daemon = True # so we can exit
    _thread.start()
    process_uploaded_student_list(student_list, client_id, absolute_uri, reg_status)

def mass_student_enroll_threaded(student_list, client_id, program_id, course_id, request, req_status):
    _thread = threading.Thread(target = _worker) # one is enough; it's postponed after all
    _thread.daemon = True # so we can exit
    _thread.start()
    process_mass_student_enroll_list(student_list, client_id, program_id, course_id, request, req_status)  

def _find_group_project_v2_blocks_in_chapter(chapter):
    return (
        (xblock, sequential, page)
        for sequential in chapter.sequentials
        for page in sequential.pages
        for xblock in page.children
        if xblock.category == GROUP_PROJECT_V2_CATEGORY
    )

def _load_course(course_id, depth=MINIMAL_COURSE_DEPTH, course_api_impl=course_api):
    '''
    Gets the course from the API, and performs any post-processing for Apros specific purposes
    '''
    def is_discussion_chapter(chapter):
        return chapter.name.startswith(settings.DISCUSSION_IDENTIFIER)

    def is_group_project_chapter(chapter):
        return chapter.name.startswith(settings.GROUP_PROJECT_IDENTIFIER)

    def is_group_project_v2_chapter(chapter):
        try:
            next(_find_group_project_v2_blocks_in_chapter(chapter))
            return True
        except StopIteration:
            return False

    def is_normal_chapter(chapter):
        '''
        Check if a chapter is normal or special. GROUP_PROJECT_WORK and DISCUSSION are special chapters.
        '''
        return (not is_discussion_chapter(chapter) and
                not is_group_project_chapter(chapter) and
                not is_group_project_v2_chapter(chapter))

    course = course_api_impl.get_course(course_id, depth)

    # Find group projects
    course.group_projects = []
    for chapter in course.chapters:
        if is_group_project_chapter(chapter):
            group_project_sequentials = [seq for seq in chapter.sequentials if is_group_activity(seq)]
            group_project = GroupProject(
                course_id, chapter.id, chapter.name[len(settings.GROUP_PROJECT_IDENTIFIER):],
                group_project_sequentials
            )
            course.group_projects.append(group_project)
        elif is_group_project_v2_chapter(chapter):
            blocks = _find_group_project_v2_blocks_in_chapter(chapter)
            projects = [
                GroupProject(
                    course_id, block.id, block.name,
                    [child for child in block.children if child.category == GROUP_PROJECT_V2_ACTIVITY_CATEGORY],
                    page.id, is_v2=True
                )
                for block, seq, page in blocks
            ]

            course.group_projects.extend(projects)

    # Only the first discussion chapter is taken into account
    course.discussion = None
    discussions = [chapter for chapter in course.chapters if chapter.name.startswith(settings.DISCUSSION_IDENTIFIER)]
    if len(discussions) > 0:
        course.discussion = discussions[0]

    course.chapters = [chapter for chapter in course.chapters if is_normal_chapter(chapter)]

    set_course_context(course, depth)

    return course


def load_course(course_id, depth=MINIMAL_COURSE_DEPTH, course_api_impl=course_api, request=None):
    """
    Gets the course from the API, and performs any post-processing for Apros specific purposes

    Args:
        course_id: str - course ID
        depth: int - course tree depth. Fetches all course tree elements down to:
            depth = 1 - course
            depth = 2 - sections
            depth = 3 - subsections
            depth = 4 - top-level xblocks
            depth = 5+ - nested xblocks up to (depth-4) level (i.e. 5 - children, 6 - children and grandchildren, etc.)
        course_api_impl: module  - implementation of course API
        request: DjangoRequest - current django request
    """
    if depth < MINIMAL_COURSE_DEPTH:
        depth = MINIMAL_COURSE_DEPTH
    course_context = get_course_context()
    if course_context and course_context.get("course_id", None) == course_id and course_context.get("depth", 0) >= depth:
        return course_context["course_content"]

    # See if we will cache courseware on the user's session
    if not getattr(settings, 'USE_SESSION_COURSEWARE_CACHING', False) or not request or not request.session:
        # simple path: load and return
        return _load_course(course_id, depth, course_api_impl)

    course = None
    if 'course_cache' in request.session:
        # see if our cached course is the same as the one wanting to be fetched
        if course_id in request.session['course_cache']:
            cache_entry = request.session['course_cache'][course_id]
            cached_time = cache_entry['time_fetched']
            fetch_depth = cache_entry['fetch_depth']

            # is the course entry too old?!?
            age = datetime.now(UTC) - cached_time

            # don't let the cache entry age indefinately
            if age.seconds < getattr(settings, 'SESSION_COURSEWARE_CACHING_EXPIRY_IN_SEC', 300) and depth <= fetch_depth:
                course = cache_entry['course_data']

    if not course:
        # actually go to the API to fetch
        course = _load_course(course_id, depth, course_api_impl)

        # if we have fetched the course, let's put it in the session cache
        if course:
            # note, since we're change the schema of the session data, we have to be able to
            # bootstrap existing sessions
            if 'course_cache' not in request.session:
                request.session['course_cache'] = {}

            request.session['course_cache'][course_id] = {
                'course_data': course,
                'transaction_counter': 0,
                'time_fetched': datetime.now(UTC),
                'fetch_depth': depth
            }

    return course


def generate_email_text_for_user_activation(activation_record, activation_link_head):
    email_text = (
        "",
        _("An administrator has created an account on McKinsey Academy for your use. To activate your account, please copy and paste this address into your web browser's address bar:"),
        "{}/{}".format(activation_link_head, activation_record.activation_key),
    )

    return '\n'.join(email_text)

def _process_line(user_line):
    try:
        fields = user_line.strip().split(',')
        # format is Email, FirstName, LastName, Title, City, Country (last 3 are optional)

        # temporarily set the user name to the first 30 characters of the allowed characters within the email
        username = re.sub(r'\W', '', fields[0])
        if len(username) > 30:
            username = username[:29]

        # Must have the first 3 fields
        user_info = {
            "email": fields[0],
            "username": username,
            "is_active": False,
            "first_name": fields[1],
            "last_name": fields[2],
            "password": settings.INITIAL_PASSWORD,
        }
        if len(fields) > 3:
            user_info["title"] = fields[3]

        if len(fields) > 4:
            user_info["city"] = fields[4]

        if len(fields) > 5:
            user_info["country"] = fields[5]

        if len(fields) > 6:
            # If password and username are included in the CSV,
            # our intent is to register and activate the user
            user_info["is_active"] = True
            user_info["password"] = fields[7]
            if fields[6]:
                user_info["username"] = fields[6]

    except Exception as e:
        user_info = {
            "error": _("Could not parse user info from {}").format(user_line)
        }

    return user_info


def _process_line_proposed(user_line):
    try:
        fields = user_line.strip().split(',')
        # format is FirstName, LastName, Email, Company, Country, City, Gender, CourseID, Status (last 3 are optional)

        # temporarily set the user name to the first 30 characters of the allowed characters within the email
        username = re.sub(r'\W', '', fields[2])
        if len(username) > 30:
            username = username[:29]

        # Must have the first 3 fields
        user_info = {
            "first_name": fields[0],
            "last_name": fields[1],
            "email": fields[2],
            "username": username,
            "is_active": False,
            "password": settings.INITIAL_PASSWORD,
        }
        if len(fields) > 3:
            user_info["company"] = fields[3]

        # COUNTRY NEEDS TO BE ENTERED AS A CODE
        # if len(fields) > 4:
        #     user_info["country"] = fields[4]

        if len(fields) > 5:
            user_info["city"] = fields[5]

        if len(fields) > 6:
            user_info["gender"] = fields[6]

        # if len(fields) > 7:
        #     # If password and username are included in the CSV,
        #     # our intent is to register and activate the user
        #     user_info["is_active"] = True
        #     user_info["password"] = fields[7]
        #     if fields[6]:
        #         user_info["username"] = fields[6]

    except Exception as e:
        user_info = {
            "error": _("Could not parse user info from {}").format(user_line)
        }

    return user_info


def _build_student_list_from_file(file_stream, parse_method=_process_line):
    # Don't need to read into a tmep file if small enough
    user_objects = []
    with tempfile.TemporaryFile() as temp_file:
        for chunk in file_stream.chunks():
            temp_file.write(chunk)

        temp_file.seek(0)

        # ignore first line
        user_objects = [parse_method(user_line) for user_line in temp_file.read().splitlines()[1:]]

    return user_objects


def _register_users_in_list(user_list, client_id, activation_link_head, reg_status):
    client = Client.fetch(client_id)
    for user_dict in user_list:
        failure = None
        user_error = None
        try:
            user = None
            activation_record = None

            try:
                user = user_api.register_user(user_dict)
            except ApiError as e:
                user = None
                failure = {
                    "reason": e.message,
                    "activity": _("Unable to register user")
                }
            if user:
                try:
                    if not user.is_active:
                        activation_record = UserActivation.user_activation(user)
                    client.add_user(user.id)
                except ApiError, e:
                    failure = {
                        "reason": e.message,
                        "activity": _("User not associated with client")
                    }

            if failure:
                user_error = _("{}: {} - {}").format(
                    failure["activity"],
                    failure["reason"],
                    user_dict["email"],
                )

        except Exception as e:
            user = None
            reason = e.message if e.message else _("Data processing error")
            user_error = _("Error processing data: {}").format(
                reason,
            )

        if user_error:
            error = UserRegistrationError.create(error=user_error, task_key=reg_status.task_key)
            reg_status.failed = reg_status.failed + 1
            reg_status.save()
        else:
            #print "\nActivation Email for {}:\n".format(user.email), generate_email_text_for_user_activation(activation_record, activation_link_head), "\n\n"
            reg_status.succeded = reg_status.succeded + 1
            reg_status.save()

def company_users_list(client_id):
    users = organization_api.get_users_by_enrolled(organization_id=client_id, user_object=user_models.UserResponse)
    return users

def enroll_user_in_course(user_id, course_id):
    try:
        user_api.enroll_user_in_course(user_id, course_id)
    except ApiError as e:
        # Ignore 409 errors, because they indicate a user already added
        if e.code != 409:
            raise

def _enroll_users_in_list(students, client_id, program_id, course_id, request, reg_status):
    client = Client.fetch(client_id)
    program = Program.fetch(program_id)
    company_users = company_users_list(client_id)
    company_users_ids = [company_user.id for company_user in company_users]

    # Not validating number of available places here, because reruns would never be able to run.
    # allocated, assigned = license_controller.licenses_report(
    #     program.id, client_id)
    # remaining = allocated - assigned

    # if len(students) > remaining:
    #     user_error = _("Not enough places available for {} program - {} left").format(program.display_name, remaining)

    for user_dict in students:
        failure = None
        user_error = []
        try:
            user = None
            activation_record = None

            try:
                user = user_api.register_user(user_dict)
            except ApiError as e:
                user = None
                failure = {
                    "reason": e.message,
                    "activity": _("Unable to register user")
                }

            if user:
                try:
                    if not user.is_active:
                        activation_record = UserActivation.user_activation(user)
                    client.add_user(user.id)
                except ApiError as e:
                    failure = {
                        "reason": e.message,
                        "activity": _("User not associated with client")
                    }

            if failure:
                user_error.append(_("{}: {} - {}").format(
                    failure["activity"],
                    failure["reason"],
                    user_dict["email"],
                ))
            try: 
                # Enroll into program
                if not user: 
                    user = user_api.get_users(email=user_dict["email"])[0]

                if (user.id in company_users_ids and failure) or not failure:
                    try:    
                        program.add_user(client_id, user.id)
                    except Exception as e:
                        user_error.append(_("{}: {} - {}").format(
                            "User program enrollment",
                            e.message,
                            user_dict["email"],
                        ))
                    try:
                        enrolled_users = {u.id:u.username for u in course_api.get_user_list(course_id) if u in students}
                        if user.id not in enrolled_users:
                            enroll_user_in_course(user.id, course_id)
                    except Exception as e: 
                        user_error.append(_("{}: {} - {}").format(
                            "User course enrollment",
                            e.message,
                            user_dict["email"],
                        ))
            except Exception as e: 
                reason = e.message if e.message else _("Enrolling student error")
                user_error.append(_("Error enrolling student: {} - {}").format(
                    reason,
                    user_dict["email"]
                ))

        except Exception as e:
            user = None
            reason = e.message if e.message else _("Data processing error")
            user_error.append(_("Error processing data: {} - {}").format(
                reason,
                user_dict["email"]
            ))

        if user_error:
            for user_e in user_error:
                error = UserRegistrationError.create(error=user_e, task_key=reg_status.task_key)
            reg_status.failed = reg_status.failed + 1
            reg_status.save()
        else:
            #print "\nActivation Email for {}:\n".format(user.email), generate_email_text_for_user_activation(activation_record, activation_link_head), "\n\n"
            reg_status.succeded = reg_status.succeded + 1
            reg_status.save() 


@postpone
def process_uploaded_student_list(file_stream, client_id, activation_link_head, reg_status=None):
    # 1) Build user list
    user_list = _build_student_list_from_file(file_stream)
    if reg_status is not None:
        reg_status.attempted = len(user_list)
        reg_status.save()
    for user_info in user_list:
        if "error" in user_info:
            UserRegistrationError.create(error=user_info["error"], task_key=reg_status.task_key)
    user_list = [user_info for user_info in user_list if "error" not in user_info]

    # 2) Register the users, and associate them with client
    _register_users_in_list(user_list, client_id, activation_link_head, reg_status)

@postpone
def process_mass_student_enroll_list(file_stream, client_id, program_id, course_id, request, reg_status=None):
    # 1) Build user list
    user_list = _build_student_list_from_file(file_stream, parse_method=_process_line_proposed)
    if reg_status is not None:
        reg_status.attempted = len(user_list)
        reg_status.save()
    for user_info in user_list:
        if "error" in user_info:
            UserRegistrationError.create(error=user_info["error"], task_key=reg_status.task_key)
    user_list = [user_info for user_info in user_list if "error" not in user_info]
    # 2) Register the users, and associate them with client
    _enroll_users_in_list(user_list, client_id, program_id, course_id, request, reg_status)


def _formatted_user_string(user):
    return u"{},{},{},{},{},{},{},{}".format(
        user.email,
        user.first_name,
        user.last_name,
        user.title,
        user.city,
        user.country,
        user.username,
        user.activation_link,
    )

def _formatted_user_string_group_list(user):
    return u"{},{},{},{}".format(
        user.email,
        user.username,
        user.first_name,
        user.last_name,
    )

def _formatted_group_string(group):
    group_string = "{} \n\n".format(
        group.name
    )

    user_list = [_formatted_user_string_group_list(user) for user in group.students]
    users_list = '\n'.join(user_list)

    group_string = group_string + users_list + '\n\n'

    return group_string

def get_student_list_as_file(client, activation_link = ''):
    user_list = client.fetch_students()
    user_strings = [_formatted_user_string(get_user_with_activation(user, activation_link)) for user in user_list]

    return '\n'.join(user_strings)

def get_user_with_activation(user, activation_link):
    try:
        activation_record = UserActivation.get_user_activation(user)
        if activation_record:
            user.activation_link = "{}/{}".format(activation_link, activation_record.activation_key)
        else:
            user.activation_link = 'Activated'
    except:
        user.activation_link = 'Could not fetch activation record'

    return user

def get_group_list_as_file(group_projects, group_project_groups):

    user_ids = []
    for group_project in group_projects:
        for group in group_project_groups[group_project.id]:
            user_ids.extend([str(u.id) for u in group.users])
    additional_fields = ['first_name','last_name']
    user_dict = {str(u.id) : u for u in user_api.get_users(ids=user_ids, fields=additional_fields)} if len(user_ids) > 0 else {}

    group_list_lines = []
    for group_project in group_projects:
        group_list_lines.append(u"{}: {}\n".format(
                _("PROJECT"),
                group_project.name.upper(),
            )
        )
        for group in group_project_groups[group_project.id]:
            group.students = [user_dict[str(u.id)] for u in group.users]
            group_list_lines.append(_formatted_group_string(group))
        group_list_lines.append("\n")

    return '\n'.join(group_list_lines)


def fetch_clients_with_program(program_id):
    clients = group_api.get_organizations_in_group(program_id, group_object=Client)
    for client in clients:
        try:
            client.places_allocated, client.places_assigned = license_controller.licenses_report(program_id, client.id)
        except:
            client.places_allocated = None
            client.places_assigned = None

    return clients

def filter_groups_and_students(group_projects, students, restrict_to_users_ids=None):

    group_project_groups = {}
    groupedStudents = []

    groups_to_hide = set()

    for group_project in group_projects:
        groups = project_api.get_project_workgroups(group_project.id, WorkGroup)

        for group in groups:
            group_users = {u.id: u for u in group.users}
            students_in_group = [s for s in students if s.id in group_users.keys()]
            groupedStudents.extend(students_in_group)

            if restrict_to_users_ids is not None:
                original_length = len(group.users)
                group.users = [user for user in group.users if user.id in restrict_to_users_ids]
                if len(group.users) != original_length:
                    groups_to_hide.add(group.id)

            for group_student in students_in_group:
                group_users[group_student.id].company = getattr(group_student, "company", None)

            group.students_count = len(group.users)

        group_project_groups[group_project.id] = [group for group in groups if group.id not in groups_to_hide]

    for student in groupedStudents:
        if student in students:
            students.remove(student)

    return group_project_groups, students

def getStudentsWithCompanies(course, restrict_to_users_ids=None):
    students = course_api.get_user_list(course.id)

    users_ids = set(user.id for user in students)
    if restrict_to_users_ids is not None:
        users_ids &= restrict_to_users_ids

    additional_fields = ["organizations"]
    students = user_api.get_users(ids=[str(user_id) for user_id in users_ids], fields=additional_fields)

    companies = {}
    for student in students:
        studentCompanies = student.organizations
        if len(studentCompanies) > 0:
            company = studentCompanies[0]
            if not company.id in companies:
                companies[company.id] = company
            student.company = companies[company.id]
    return students, companies


def parse_studentslist_from_post(postValues):

    students = []
    i = 0
    project_id = None
    try:
        project_id = postValues['project_id']
        while(postValues['students[{}]'.format(i)]):
            students.append({'id': postValues['students[{}]'.format(i)],
                            'company_id': postValues['students[{}][data_field]'.format(i)]})
            i = i + 1
    except:
        pass

    return students, project_id

def is_group_activity(activity):
    if activity.category == GROUP_PROJECT_V2_ACTIVITY_CATEGORY:
        return True
    return len(activity.pages) > 0 and GROUP_PROJECT_CATEGORY in activity.pages[0].child_category_list()

def get_group_activity_xblock(activity):
    if activity.category == GROUP_PROJECT_V2_ACTIVITY_CATEGORY:
        return activity
    return [gp for gp in activity.pages[0].children if gp.category == GROUP_PROJECT_CATEGORY][0]


def generate_course_report(client_id, course_id, url_prefix, students):

    output_lines = []

    client = Client.fetch(client_id)

    def zero_if_none(obj, name):
        value = getattr(obj, name, 0)
        return value if value is not None else 0

    def prepare_value(obj, name):
        value = getattr(obj, name, None)
        """
        Fields that contain commas, quotes, and CR/LF need to be wrapped in double-quotes.
        If double-quotes are used to enclose fields, then a double-quote appearing inside a field must be escaped
        by preceding it with another double quote.
        """
        return '"{}"'.format(value.replace('"', '""')) if value is not None else ''

    def output_line(line_data_array):
        output_lines.append(','.join(line_data_array))

    activity_names_row = ["Client Name","","Course ID",""]
    output_line(activity_names_row)

    group_header_row = [client.name,"", course_id]
    output_line(group_header_row)

    output_line("--------")

    activity_names_row = ["Full Name","Username","Title","Email", "Progress %", "Engagement", "Proficiency", "Course Completed"]
    output_line(activity_names_row)

    for student in students:
        user_row = [
            prepare_value(student, "full_name"),
            prepare_value(student, "username"),
            prepare_value(student, "title"),
            prepare_value(student, "email"),
            "{}%".format(str(zero_if_none(student, "progress"))),
            str(zero_if_none(student, "engagement")),
            str(zero_if_none(student, "proficiency")),
            str(prepare_value(student, "completed"))
        ]
        output_line(user_row)

    return '\n'.join(output_lines)


def get_organizations_users_completion(client_id, course_id, users_enrolled):
    users_completed = organization_api.get_grade_complete_count(client_id, courses=course_id).users_grade_complete_count
    percent_completed = '0%'
    if users_enrolled > 0:
        percent_completed = "{}%".format(int((float(users_completed) / float(users_enrolled)) * 100))
    return users_completed, percent_completed


def get_course_metrics_for_organization(course_id, client_id):
    metrics = course_api.get_course_metrics(course_id, organization=client_id)
    org_metrics = organization_api.get_grade_complete_count(client_id, courses=course_id)
    metrics.users_grade_complete_count = org_metrics.users_grade_complete_count
    metrics.users_grade_average = org_metrics.users_grade_average
    metrics.percent_completed = 0
    if metrics.users_enrolled:
        metrics.percent_completed = int(float(metrics.users_grade_complete_count) / int(metrics.users_enrolled) * 100)
    return metrics

def get_course_analytics_progress_data(course, course_modules, client_id=None):
    if client_id:
        users_count = len(course_api.get_users_list_in_organizations(course.id, client_id))
    else:
        users_count = len(course_api.get_user_list(course.id))
    total = users_count * len(course_modules)
    start_date = course.start
    end_date = datetime.now()
    if course.end is not None:
        if end_date > course.end:
            end_date = course.end
    if client_id:
        metrics = course_api.get_course_time_series_metrics(course.id, start_date, end_date, organization=client_id)
    else:
        metrics = course_api.get_course_time_series_metrics(course.id, start_date, end_date)
    metricsJson = [[0,0]]
    day = 1
    mod_completed = 0
    for i, metric in enumerate(metrics.modules_completed):
        mod_completed += metrics.modules_completed[i][1]
        metricsJson.append([day, round((float(mod_completed) / total * 100), 2)])
        day += 1

    return metricsJson

def get_course_details_progress_data(course, course_modules, users):

    start_date = course.start
    end_date = datetime.now()
    if course.end is not None:
        if end_date > course.end:
            end_date = course.end
    delta = end_date - start_date
    metrics = course_api.get_course_time_series_metrics(course.id, start_date, end_date, interval='days')

    total = len(users) * len(course_modules)
    engaged_total = 0

    course_metrics = course_api.get_course_metrics_completions(course.id, count=total)
    course_leaders_ids = [leader.id for leader in course_metrics.leaders]
    for course_user in users:
        if course_user.id in course_leaders_ids:
            engaged_total += 1

    engaged_total = engaged_total * len(course_modules)

    metricsJsonAll = [[0,0]]
    metricsJsonEng = [[0,0]]

    day = 1
    mod_completed = 0
    for i, metric in enumerate(metrics.modules_completed):
        mod_completed += metrics.modules_completed[i][1]
        if total:
            metricsJsonAll.append([day, round((float(mod_completed) * 100 / total), 2)])
        else:
            metricsJsonAll.append([day, 0])
        if engaged_total:
            metricsJsonEng.append([day, round((float(mod_completed) * 100 / engaged_total), 2)])
        else:
            metricsJsonEng.append([day, 0])
        day += 1

    return metricsJsonAll, metricsJsonEng

def get_contacts_for_client(client_id):
    groups = Client.fetch_contact_groups(client_id)

    contacts = []
    fields = ['phone', 'full_name', 'title', 'avatar_url']

    for group in groups:
        if group.type == "contact_group":
            users = group_api.get_users_in_group(group.id)
            if len(users) > 0:
                user_ids = [str(user.id) for user in users]
                contacts.extend(user_api.get_users(fields=fields, ids=(',').join(user_ids)))

    return contacts

def get_admin_users(organizations, org_id, ADMINISTRATIVE):

    users = []
    additional_fields = ["organizations"]

    if org_id == ADMINISTRATIVE:
        # fetch users users that have no company association
        users = user_api.get_users(has_organizations=False, fields=additional_fields)

        # fetch users in administrative company
        admin_company = next((org for org in organizations if org.name == settings.ADMINISTRATIVE_COMPANY), None)
        admin_users = []
        if admin_company and admin_company.users:
            ids = [str(id) for id in admin_company.users]
            admin_users = user_api.get_users(ids=ids,fields=additional_fields)

        users.extend(admin_users)

    else:
        org = next((org for org in organizations if org.id == org_id), None)
        if org:
            ids = [str(id) for id in org.users]
            users = user_api.get_users(ids=ids, fields=additional_fields)

    return users

def get_program_data_for_report(client_id, program_id=None):
    programs = Client.fetch(client_id).fetch_programs()
    program = next((p for p in programs if p.id == program_id), programs[0])
    program_courses = program.fetch_courses()
    course_ids = list(set([pc.course_id for pc in program_courses]))
    courses = course_api.get_courses(course_id=course_ids)

    for course in courses:
        course.metrics = get_course_metrics_for_organization(course.id, client_id)

    total_avg_grade = 0
    total_pct_completed = 0
    if courses:
        count = float(len(courses))
        total_avg_grade = sum([c.metrics.users_grade_average for c in courses]) / count
        total_pct_completed = sum([c.metrics.percent_completed for c in courses]) / count

    return program, courses, total_avg_grade, total_pct_completed


def generate_access_key():
    ''' Generate a unique url-friendly code. '''
    return str(uuid.uuid4())


def get_accessible_programs(user, restrict_to_programs_ids):
    programs = Program.list()
    if restrict_to_programs_ids:
        programs = [
            program for program in programs
            if program.id in restrict_to_programs_ids
    ]

    if not any([user.is_mcka_admin, user.is_client_admin, user.is_internal_admin]):
        # User is a TA. They'll need to be scoped only to the courses they're a TA on, not just enrolled in.
        roles = user.get_roles()
        base_programs = programs
        programs = []
        for program in base_programs:
            for course in program.fetch_courses():
                if USER_ROLES.TA in [role.role for role in roles if role.course_id == course.course_id]:
                    programs.append(program)
                    break

    return programs


def get_accessible_courses_from_program(user, program_id, restrict_to_courses_ids=None):
    program = Program.fetch(program_id)
    courses = program.fetch_courses()
    if not any([user.is_client_admin, user.is_mcka_admin, user.is_internal_admin]):
        roles = user.get_roles()
        # User is TA. Only show courses in program they have access to.
        courses = [
            course for course in courses if USER_ROLES.TA in [
                role.role for role in roles if role.course_id == course.course_id
                ]
            ]

    if restrict_to_courses_ids:
        courses = [course for course in courses if course.course_id in restrict_to_courses_ids]

    return courses


def load_group_projects_info_for_course(course, companies):
    group_project_lookup = {gp.id: gp.name for gp in course.group_projects}
    group_projects = []
    for project in Project.fetch_projects_for_course(course.id):
        try:
            project_name = group_project_lookup[project.content_id]
            project_status = True
        except:
            project_name = project.content_id
            project_status = False

        if project.organization is None:
            group_projects.append(
                GroupProjectInfo(
                    project.id,
                    project_name,
                    project_status
                )
            )
        else:
            group_projects.append(
                GroupProjectInfo(
                    project.id,
                    project_name,
                    project_status,
                    companies[project.organization].display_name,
                    companies[project.organization].id,
                )
            )

    return group_projects


class GroupProjectInfo(object):
    def __init__(self, id, name, status, organization=None, organization_id=0):
        self.id = id
        self.name = name
        self.status = status
        self.organization = organization
        self.organization_id = organization_id


_QuickLinkWithRelatedObjs = collections.namedtuple(
    "_QuickLinkWithRelatedObjs", ['quick_link', 'program', 'course', 'group_work', 'client']
)

def _get_quick_link_related_objects(quick_link):

    """
    Queries API for object relatred with this quick link

    Args:
        quick_link: DashboardAdminQuickFilter

    Returns: _QuickLinkWithRelatedObjs
    """

    program = Program.fetch(quick_link.program_id)
    course = None
    group_work = None
    client = None

    # Course id can be an empty string which also (I guess) means empty,
    # so no is None here
    if quick_link.course_id:
        course = load_course(quick_link.course_id)

    # GP id can be an empty string which also (I guess) means empty,
    # so no is None here
    if quick_link.course_id and quick_link.group_work_project_id:
        group_projects = [
            gp
            for gp in course.group_projects
            if gp.is_v2 and gp.id == quick_link.group_work_project_id
        ]

        # If group project can't be found we'll return quick link without
        # the group project
        if len(group_projects) > 0:
             group_work = group_projects[0]

    if quick_link.company_id is not None:
        client = Client.fetch(quick_link.company_id)
        client  = client

    return _QuickLinkWithRelatedObjs(
        quick_link=quick_link, course=course, program=program,
        group_work=group_work, client=client
    )


def serialize_quick_link(quick_link):
    """
    Serializes quick link and associated objects to a dictionary.

    Args:
        quick_link - DashboardAdminQuickFilter

    Returns: json serializable dictionary
    """
    related = _get_quick_link_related_objects(quick_link)

    serialized = {
        "id": quick_link.pk,
        "program": {
            "display_name": related.program.display_name,
            "id": related.program.id
        }
    }

    if related.course is not None:
        serialized["course"] = {
            "display_name": related.course.name,
            "id": related.course.id
        }

    if related.group_work is not None:
        serialized["group_work"] = {
            "display_name": related.group_work.name,
            "id": related.group_work.id,
        }

    if related.client is not None:
        serialized['client'] = {
            "display_name": related.client.display_name,
            "id": related.client.id
        }

    return serialized


def round_to_int(value):
    return int(round(value))


def round_to_int_bump_zero(value):
    rounded_value = round_to_int(value)
    if rounded_value < 1 and value > 0:
        rounded_value = 1
    return rounded_value


def get_course_social_engagement(course_id):

    course_users_simple = course_api.get_user_list(course_id)
    course_users_ids = [str(user.id) for user in course_users_simple]
    roles = course_api.get_users_filtered_by_role(course_id)
    roles_ids = [str(user.id) for user in roles]
    for role_id in roles_ids:
        if role_id in course_users_ids: course_users_ids.remove(role_id)

    number_of_users = len(course_users_ids)

    number_of_posts = 0
    number_of_participants_posting = 0
    course_metrics_social = course_api.get_course_details_metrics_social(course_id)

    for user in course_metrics_social['users']:
        user_data = course_metrics_social['users'][str(user)]
        number_of_participants_posting += 1
        number_of_posts_per_participant = user_data['num_threads'] + user_data['num_replies'] + user_data['num_comments']
        number_of_posts += number_of_posts_per_participant

    if number_of_users:
        participants_posting = str(round_to_int_bump_zero(float(number_of_participants_posting)*100/number_of_users)) + '%'
        avg_posts = round(float(number_of_posts)/number_of_users, 1)
    else:
        participants_posting = 0
        avg_posts = 0

    course_stats = [
        { 'name': '# of posts', 'value': number_of_posts},
        { 'name': '% participants posting', 'value': participants_posting},
        { 'name': 'Avg posts per participant', 'value': avg_posts}
    ]

    return course_stats


def get_course_engagement_summary(course_id):

    course_users_simple = course_api.get_user_list(course_id)
    course_users_ids = [str(user.id) for user in course_users_simple]
    roles = course_api.get_users_filtered_by_role(course_id)
    roles_ids = [str(user.id) for user in roles]
    for role_id in roles_ids:
        if role_id in course_users_ids: course_users_ids.remove(role_id)

    additional_fields = ["is_active"]
    course_users = user_api.get_users(ids=course_users_ids, fields=additional_fields)
    course_metrics = course_api.get_course_metrics_completions(course_id, count=len(course_users_simple))
    course_leaders_ids = [leader.id for leader in course_metrics.leaders]

    active_users = 0
    engaged_users = 0
    engaged_progress_sum = sum([leader.completions for leader in course_metrics.leaders])
    for course_user in course_users:
        if course_user.is_active is True:
            active_users += 1
        if course_user.id in course_leaders_ids:
            engaged_users += 1

    course_progress = round_to_int_bump_zero(float(engaged_progress_sum)/len(course_users_simple)) if len(course_users_simple) > 0 else 0
    activated = round_to_int_bump_zero((float(active_users)/len(course_users)) * 100) if len(course_users) > 0 else 0
    engaged = round_to_int_bump_zero((float(engaged_users)/len(course_users)) * 100) if len(course_users) > 0 else 0
    active_progress = round_to_int_bump_zero(float(engaged_progress_sum)/active_users) if active_users > 0 else 0
    engaged_progress = round_to_int_bump_zero(float(engaged_progress_sum)/engaged_users) if engaged_users > 0 else 0

    course_stats = [
         { 'name': 'Total Cohort', 'people': len(course_users), 'invited': '-', 'progress': str(course_progress) + '%'},
         { 'name': 'Activated', 'people': active_users, 'invited': str(activated) + '%', 'progress': str(active_progress) + '%'},
         { 'name': 'Engaged', 'people': engaged_users, 'invited': str(engaged) + '%', 'progress': str(engaged_progress) + '%'},
         { 'name': 'Logged in over last 7 days', 'people': 'N/A', 'invited': 'N/A', 'progress': 'N/A'}
    ]

    return course_stats


def course_bulk_actions(course_id, data, batch_status):
    batch_status.clean_old()
    _thread = threading.Thread(target = _worker) # one is enough; it's postponed after all
    _thread.daemon = True # so we can exit
    _thread.start()
    course_bulk_action(course_id, data, batch_status)


@postpone
def course_bulk_action(course_id, data, batch_status):
    if (data['type'] == 'status_change'):
        if batch_status is not None:
            batch_status.attempted = len(data['list_of_items'])
            batch_status.save()
        for status_item in data['list_of_items']:
            status = change_user_status(course_id, data['new_status'], status_item)
            if (status['status']=='error'):
                if batch_status is not None:
                    batch_status.failed = batch_status.failed + 1
                    batch_status.save()    
                    BatchOperationErrors.create(error=status["message"], task_key=batch_status.task_key, user_id=int(status_item['id']))
            elif (status['status']=='success'):
                if batch_status is not None:
                    batch_status.succeded = batch_status.succeded + 1
                    batch_status.save()
    elif (data['type'] == 'unenroll_participants'):
        if batch_status is not None:
            batch_status.attempted = len(data['list_of_items'])
            batch_status.save()
        for status_item in data['list_of_items']:
            status = unenroll_participant(course_id, status_item)
            if (status['status']=='error'):
                if batch_status is not None:
                    batch_status.failed = batch_status.failed + 1
                    batch_status.save()    
                    BatchOperationErrors.create(error=status["message"], task_key=batch_status.task_key, user_id=int(status_item['id']))
            elif (status['status']=='success'):
                if batch_status is not None:
                    batch_status.succeded = batch_status.succeded + 1
                    batch_status.save()    
    elif (data['type'] == 'enroll_participants'):
        if batch_status is not None:
            batch_status.attempted = len(data['list_of_items'])
            batch_status.save()
        for status_item in data['list_of_items']:
            status = _enroll_participant_with_status(data['course_id'], status_item['id'], data['new_status'])
            if (status['status']=='error'):
                if batch_status is not None:
                    batch_status.failed = batch_status.failed + 1
                    batch_status.save()    
                    BatchOperationErrors.create(error=status["message"], task_key=batch_status.task_key, user_id=int(status_item['id']))
            elif (status['status']=='success'):
                if batch_status is not None:
                    batch_status.succeded = batch_status.succeded + 1
                    batch_status.save()    


def _enroll_participant_with_status(course_id, user_id, status):
    permissonsMap = {
        'TA': USER_ROLES.TA,
        'Observer': USER_ROLES.OBSERVER
    }
    failure = None
    try:
        user_api.enroll_user_in_course(user_id, course_id)
    except ApiError as e: 
        failure = {
            "status": 'error',
            "message": e.message
        }
    if failure:
        return {'status':'error', 'message':e.message}
    try:
        permissions = Permissions(user_id)
        if status != 'Active' :
            permissions.update_course_role(course_id,permissonsMap[status])
    except ApiError as e:
        failure = {
            "status": 'error',
            "message": e.message
        }
    if failure:
        return {'status':'error', 'message':e.message}

    return {'status':'success'}

         
def unenroll_participant(course_id, user_id):
    try:
        permissions = Permissions(user_id)
        permissions.remove_all_course_roles(course_id)
        user_groups = user_api.get_user_workgroups(user_id,course_id)
        for group in user_groups:
            workgroup_api.remove_user_from_workgroup(vars(group)['id'], user_id)
        user_api.unenroll_user_from_course(user_id, course_id)
    except ApiError as e:
        return {'status':'error', 'message':e.message}
    return {'status':'success'}


def change_user_status(course_id, new_status, status_item):
    permissonsMap = {
        'TA': USER_ROLES.TA,
        'Observer': USER_ROLES.OBSERVER
    }
    if new_status not in status_item['existing_roles']:
        try:
            permissions = Permissions(status_item['id'])
            if new_status != 'Active' :
                permissions.update_course_role(course_id,permissonsMap[new_status])
            else:
                permissions.remove_all_course_roles(course_id)
        except ApiError as e:
            return {'status':'error', 'message':e.message}
    return {'status':'success'}


def get_course_users_roles(course_id, permissions_filter_list):
    course_roles_users = course_api.get_users_filtered_by_role(course_id)
    user_roles_list = {'ids':[],'data':[]}
    for course_role in course_roles_users:
        roleData = vars(course_role)
        if permissions_filter_list:
            if roleData['role'] in permissions_filter_list:
                user_roles_list['data'].append(roleData)
                user_roles_list['ids'].append(str(roleData['id']))
        else:
            user_roles_list['data'].append(roleData)
            user_roles_list['ids'].append(str(roleData['id']))
    user_roles_list['ids'] = set(user_roles_list['ids'])
    user_roles_list['ids'] = list(user_roles_list['ids'])
    return user_roles_list

def get_user_courses_helper(user_id):

    user_courses = []
    allCourses = user_api.get_courses_from_user(user_id)
    for course in allCourses:
        user_course = {}
        user_course['name'] = course['name']
        user_course['id'] = course['id']
        user_course['program'] = '-'
        user_course['progress'] = "."
        user_course['proficiency'] = "."
        user_course['completed'] ='N/A'
        user_course['grade'] ='N/A'
        user_course['status'] = 'Active'
        user_course['unenroll'] = 'Unenroll'
        user_course['start'] = course['start']
        if course['end'] is not None:
            user_course['end'] = course['end']
        else: 
            user_course['end'] = '-'
        user_courses.append(user_course)
    user_roles = user_api.get_user_roles(user_id)
    for role in user_roles:
        if not any(item['id'] == vars(role)['course_id'] for item in user_courses):
            course = course_api.get_course_details(vars(role)['course_id'])
            user_course = {}
            user_course['name'] = course['name']
            user_course['id'] = course['id']
            user_course['program'] = '-'
            user_course['progress'] = "."
            user_course['proficiency'] = "."
            user_course['completed'] ='N/A'
            user_course['grade'] ='N/A'
            user_course['start'] = course['start']
            if course['end'] is not None:
                user_course['end'] = course['end']
            else: 
                user_course['end'] = '-'
            if vars(role)['role'] == 'observer':
                user_course['status'] = 'Observer'
            if vars(role)['role'] == 'assistant':
                user_course['status'] = 'TA'
            user_course['unenroll'] = 'Unenroll'
            user_courses.append(user_course)       
        else:
            user_course = (user_course for user_course in user_courses if user_course["id"] == vars(role)['course_id']).next()
            if user_course['status'] != 'TA':
                if vars(role)['role'] == 'observer':
                    user_course['status'] = 'Observer'
                if vars(role)['role'] == 'assistant':
                    user_course['status'] = 'TA'

    active_courses = []
    course_history = []    
    for user_course in user_courses:
        if timezone.now() >= parsedate(user_course['start']):
            if user_course['end'] == '-':
                active_courses.append(user_course)
            elif timezone.now() <= parsedate(user_course['end']):
                active_courses.append(user_course)
            else:
                course_history.append(user_course)

    return active_courses, course_history
    
def get_course_progress(course_id, users, request):
    '''
    Helper method for calculating user pogress on course. 
    Returns dictionary of users with user_id and progress.
    '''
    course = None
    course = load_course(course_id, request=request)

    users_progress = []
    user_completions = []
    for user in users:
        user_completion = {}
        user_completion['user_id'] = user['id']
        user_completion['results'] = []
        user_completions.append(user_completion)

    completions = course_api.get_completions_on_course(course.id)

    for completion in completions:
        for user_completion in user_completions:
            if completion['user_id'] == user_completion['user_id']:
                user_completion['results'].append(completion)

    for user_completion in user_completions:
        user_progress = {}
        user_progress['user_id'] = user_completion['user_id']
        completed_ids = [result['content_id'] for result in user_completion['results']]
        component_ids = course.components_ids(settings.PROGRESS_IGNORE_COMPONENTS)
        for lesson in course.chapters:
            lesson.progress = 0
            lesson_component_ids = course.lesson_component_ids(lesson.id, completed_ids,
                                                               settings.PROGRESS_IGNORE_COMPONENTS)
            if len(lesson_component_ids) > 0:
                matches = set(lesson_component_ids).intersection(completed_ids)
                lesson.progress = round_to_int(100 * len(matches) / len(lesson_component_ids))
        actual_completions = set(component_ids).intersection(completed_ids)
        actual_completions_len = len(actual_completions)
        component_ids_len = len(component_ids)
        try:
            user_progress['progress'] = round_to_int(float(100 * actual_completions_len)/component_ids_len)
        except ZeroDivisionError:
            user_progress['progress'] = 0
        users_progress.append(user_progress)

    return users_progress


def import_participants_threaded(student_list, request, req_status):
    _thread = threading.Thread(target = _worker) # one is enough; it's postponed after all
    _thread.daemon = True # so we can exit
    _thread.start()
    process_import_participants_list(student_list, request, req_status)  


@postpone
def process_import_participants_list(file_stream, request, reg_status=None):
    # 1) Build user list
    user_list = _build_student_list_from_file(file_stream, parse_method=_process_line_participants_csv)
    if reg_status is not None:
        reg_status.attempted = len(user_list)
        reg_status.save()
    for user_info in user_list:
        if "error" in user_info:
            UserRegistrationError.create(error=user_info["error"], task_key=reg_status.task_key)
    user_list = [user_info for user_info in user_list if "error" not in user_info]
    # 2) Register the users, and associate them with client
    _enroll_participants_from_csv(user_list, request, reg_status)


def _process_line_participants_csv(user_line):
    try:
        fields = user_line.strip().split(',')
        # format is FirstName, LastName, Email, Company, CourseID, Status

        # temporarily set the user name to the first 30 characters of the allowed characters within the email
        username = re.sub(r'\W', '', fields[2])
        if len(username) > 30:
            username = username[:29]

        user_info = {
            "first_name": fields[0],
            "last_name": fields[1],
            "email": fields[2],
            "company": fields[3],
            "course": fields[4],
            "status": fields[5],
            "username": username,
            "is_active": False,
            "password": settings.INITIAL_PASSWORD,
        }

    except Exception as e:
        user_info = {
            "error": _("Could not parse user info from {}").format(user_line)
        }

    return user_info


def _enroll_participants_from_csv(students, request, reg_status):

    permissonsMap = {
        'ta': USER_ROLES.TA,
        'observer': USER_ROLES.OBSERVER
    }

    for user_dict in students:

        client_id = user_dict['company']
        client = None
        course_id = user_dict['course']
        status = user_dict['status'].lower()

        failure = None
        user_error = []
        try:
            user = None
            activation_record = None

            try:
                user = user_api.register_user(user_dict)
            except ApiError as e:
                user = None
                failure = {
                    "reason": e.message,
                    "activity": _("Unable to register user")
                }

            if user:
                try: 
                    client = Client.fetch(client_id)
                except ApiError as e:
                    failure = {
                        "reason": e.message,
                        "activity": _("Non existing Client")
                    }
                try:
                    if not user.is_active:
                        activation_record = UserActivation.user_activation_by_task_key(user, reg_status.task_key, client_id)
                    if client:
                        client.add_user(user.id)
                except ApiError as e:
                    failure = {
                        "reason": e.message,
                        "activity": _("User not associated with client")
                    }

            if failure:
                user_error.append(_("{}: {} - {}").format(
                    failure["activity"],
                    failure["reason"],
                    user_dict["email"],
                ))
            try: 
                # Add User to course
                if not user: 
                    user = user_api.get_users(email=user_dict["email"])[0]

                try:
                    enrolled_users = {u.id:u.username for u in course_api.get_user_list(course_id) if u in students}
                    if user.id not in enrolled_users:
                        enroll_user_in_course(user.id, course_id)
                except Exception as e: 
                    user_error.append(_("{}: {} - {}").format(
                        "User course enrollment",
                        e.message,
                        user_dict["email"],
                    ))

                try:
                    permissions = Permissions(user.id)
                    if status != 'active' :
                        permissions.update_course_role(course_id,permissonsMap[status])
                except ApiError as e:
                    user_error.append(_("{}: {} - {}").format(
                        "User course status",
                        e.message,
                        user_dict["email"],
                    ))
                    
            except Exception as e: 
                reason = e.message if e.message else _("Enrolling student error")
                user_error.append(_("Error enrolling student: {} - {}").format(
                    reason,
                    user_dict["email"]
                ))

        except Exception as e:
            user = None
            reason = e.message if e.message else _("Data processing error")
            user_error.append(_("Error processing data: {} - {}").format(
                reason,
                user_dict["email"]
            ))

        if user_error:
            for user_e in user_error:
                error = UserRegistrationError.create(error=user_e, task_key=reg_status.task_key)
            reg_status.failed = reg_status.failed + 1
            reg_status.save()
        else:
            #print "\nActivation Email for {}:\n".format(user.email), generate_email_text_for_user_activation(activation_record, activation_link_head), "\n\n"
            reg_status.succeded = reg_status.succeded + 1
            reg_status.save() 

def _send_activation_email_to_single_new_user(activation_record, user, absolute_uri):
    msg = [email_add_single_new_user(absolute_uri, user, activation_record)]
    result = sendMultipleEmails(msg)
    print result

def get_learner_dashboard_flag(course_id):
    try:
        learner_dashboard_flag = FeatureFlags.objects.get(course_id=course_id).learner_dashboard
    except:
        learner_dashboard_flag = False

    return learner_dashboard_flag
