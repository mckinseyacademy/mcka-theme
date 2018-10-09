import Queue
import StringIO
import atexit
import collections
import csv
import logging
import string
import tempfile
import threading
import urllib
import uuid
from datetime import datetime

import re
from PIL import Image
from bs4 import BeautifulSoup
from dateutil.parser import parse as parsedate
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.core.validators import validate_email, ValidationError
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import ugettext as _
from pytz import UTC
from rest_framework import status
from rest_framework.response import Response

from accounts.helpers import get_user_activation_links, get_complete_country_name
from accounts.middleware.thread_local import set_course_context, get_course_context
from accounts.models import UserActivation
from admin.forms import MobileBrandingForm
from admin.models import Program, SelfRegistrationRoles, ClientCustomization
from api_client import (
    course_api,
    course_models,
    group_api,
    oauth2_requests,
    organization_api,
    project_api,
    user_api,
    user_models,
    workgroup_api,
    manager_api
)
from api_client.api_error import ApiError
from api_client.group_api import PERMISSION_GROUPS
from api_client.group_api import TAG_GROUPS
from api_client.mobileapp_api import create_mobile_app_theme, get_mobile_app_themes, update_mobile_app_theme
from api_client.organization_api import get_organization_fields
from api_client.project_models import Project
from api_client.user_api import USER_ROLES, update_user_company_field_values, get_company_fields_value_for_user
from courses.models import FeatureFlags, CourseMetaData
from lib.mail import (
    sendMultipleEmails, email_add_single_new_user, create_multiple_emails
)
from lib.utils import DottableDict
from license import controller as license_controller
from util.data_sanitizing import sanitize_data, clean_xss_characters, remove_characters, special_characters_match
from util.validators import validate_first_name, validate_last_name, RoleTitleValidator, normalize_foreign_characters
from .models import (
    Client, WorkGroup, UserRegistrationError, BatchOperationErrors, WorkGroupActivityXBlock,
    GROUP_PROJECT_CATEGORY, GROUP_PROJECT_V2_CATEGORY,
    GROUP_PROJECT_V2_ACTIVITY_CATEGORY, EmailTemplate
)
from .permissions import Permissions, SlimAddingPermissions

# need to load everything up to first level nested XBlocks to properly get Group Project V2 activities
MINIMAL_COURSE_DEPTH = 5
# need to load one level more deep to get Group Project V2 stages as their close dates are needed for report
GROUP_WORK_REPORT_DEPTH = 6

_logger = logging.getLogger(__name__)


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
                activity.xblock = WorkGroupActivityXBlock.fetch_from_activity(self.course_id, activity.id, self.is_v2)

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
            pass  # bork or ignore here; ignore for now
        finally:
            _queue.task_done()  # so we can join at exit


def postpone(func):
    def decorator(*args, **kwargs):
        _queue.put((func, args, kwargs))

    return decorator


def _cleanup():
    _queue.join()  # so we don't exit too soon


_queue = Queue.Queue()
atexit.register(_cleanup)


def upload_student_list_threaded(student_list, client_id, absolute_uri, reg_status):
    _thread = threading.Thread(target=_worker)  # one is enough; it's postponed after all
    _thread.daemon = True  # so we can exit
    _thread.start()
    process_uploaded_student_list(student_list, client_id, absolute_uri, reg_status)


def mass_student_enroll_threaded(student_list, client_id, program_id, course_id, request, reg_status):
    _thread = threading.Thread(target=_worker)  # one is enough; it's postponed after all
    _thread.daemon = True  # so we can exit
    _thread.start()
    process_mass_student_enroll_list(student_list, client_id, program_id, course_id, request, reg_status)


def _find_group_project_v2_blocks_in_chapter(chapter):
    return (
        (xblock, sequential, page)
        for sequential in chapter.sequentials
        for page in sequential.pages
        for xblock in page.children
        if xblock.category == GROUP_PROJECT_V2_CATEGORY
    )


def _load_course(course_id, depth=MINIMAL_COURSE_DEPTH, course_api_impl=course_api, user=None):
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

    course = course_api_impl.get_course(course_id, depth, user=user)

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


def load_course(course_id, depth=MINIMAL_COURSE_DEPTH, course_api_impl=course_api, request=None, enable_cache=True):
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
    if (
            course_context and
            course_context.get("course_id", None) == course_id and
            course_context.get("depth", 0) >= depth
    ):
        return course_context["course_content"]

    user = request.user if request else None

    # See if we will cache courseware on the user's session
    if (
            not getattr(settings, 'USE_SESSION_COURSEWARE_CACHING', False) or
            not request or
            not request.session
    ):
        # simple path: load and return
        return _load_course(course_id, depth, course_api_impl, user=user)

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
            if age.seconds < getattr(settings, 'SESSION_COURSEWARE_CACHING_EXPIRY_IN_SEC',
                                     300) and depth <= fetch_depth:
                course = cache_entry['course_data']

    if not course:
        # actually go to the API to fetch
        course = _load_course(course_id, depth, course_api_impl, user=user)

        # if we have fetched the course, let's put it in the session cache
        if course and enable_cache:
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
        _(
            "An administrator has created an account on McKinsey Academy for your use. To activate your account, please copy and paste this address into your web browser's address bar:"),
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
            "error": _("Could not parse user info from {user_line}").format(user_line=user_line)
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
            "error": _("Could not parse user info from {user_line}").format(user_line=user_line)
        }

    return user_info


def build_student_list_from_file(file_stream, parse_method=_process_line):
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
            user_error = _("Error processing data: {reason}").format(reason=reason)

        if user_error:
            error = UserRegistrationError.create(error=user_error, task_key=reg_status.task_key)
            reg_status.failed = reg_status.failed + 1
            reg_status.save()
        else:
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
                user_error.append("{activity}: {reason} - {email)".format(
                    activity=failure["activity"],
                    failure=failure["reason"],
                    email=user_dict["email"],
                ))
            try:
                # Enroll into program
                if not user:
                    user = user_api.get_users(email=user_dict["email"])[0]

                if (user.id in company_users_ids and failure) or not failure:
                    try:
                        program.add_user(client_id, user.id)
                    except Exception as e:
                        user_error.append(_("{error}: {message} - {email}").format(
                            error=_("User program enrollment"),
                            message=e.message,
                            email=user_dict["email"],
                        ))
                    try:
                        enroll_user_in_course(user.id, course_id)
                    except Exception as e:
                        user_error.append(_("{error}: {message} - {email}").format(
                            error=_("User course enrollment"),
                            message=e.message,
                            email=user_dict["email"],
                        ))
            except Exception as e:
                reason = e.message if e.message else _("Enrolling student error")
                user_error.append(_("Error enrolling student: {reason} - {email}").format(
                    reason=reason,
                    email=user_dict["email"]
                ))

        except Exception as e:
            user = None
            reason = e.message if e.message else _("Data processing error")
            user_error.append(_("Error processing data: {reason} - {email}").format(
                reason=reason,
                email=user_dict["email"]
            ))

        if user_error:
            for user_e in user_error:
                error = UserRegistrationError.create(error=user_e, task_key=reg_status.task_key)
            reg_status.failed = reg_status.failed + 1
            reg_status.save()
        else:
            reg_status.succeded = reg_status.succeded + 1
            reg_status.save()


@postpone
def process_uploaded_student_list(file_stream, client_id, activation_link_head, reg_status=None):
    # 1) Build user list
    user_list = build_student_list_from_file(file_stream)
    if reg_status is not None:
        reg_status.attempted = len(user_list)
        reg_status.save()
    for user_info in user_list:
        if "error" in user_info:
            UserRegistrationError.create(error=user_info["error"], task_key=reg_status.task_key)
            reg_status.failed = reg_status.failed + 1
            reg_status.save()
    user_list = [user_info for user_info in user_list if "error" not in user_info]

    # 2) Register the users, and associate them with client
    _register_users_in_list(user_list, client_id, activation_link_head, reg_status)


@postpone
def process_mass_student_enroll_list(file_stream, client_id, program_id, course_id, request, reg_status=None):
    # 1) Build user list
    user_list = build_student_list_from_file(file_stream, parse_method=_process_line_proposed)
    if reg_status is not None:
        reg_status.attempted = len(user_list)
        reg_status.save()
    for user_info in user_list:
        if "error" in user_info:
            UserRegistrationError.create(error=user_info["error"], task_key=reg_status.task_key)
            reg_status.failed = reg_status.failed + 1
            reg_status.save()
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


def _formatted_user_array(user):
    return [
        user.email,
        user.first_name,
        user.last_name,
        user.title,
        user.city,
        user.country,
        user.username,
        user.activation_link,
    ]


def _formatted_user_string_group_list(user):
    # apply csv cleaning
    user_data = sanitize_data(data=user.to_dict(), props_to_clean=settings.USER_PROPERTIES_TO_CLEAN)

    return u"{},{},{},{}".format(
        user_data.get('email', ''),
        user_data.get('username', ''),
        user_data.get('first_name', ''),
        user_data.get('last_name', ''),
    )


def _formatted_group_string(group):
    group_string = "{} \n\n".format(
        group.name
    )

    user_list = [_formatted_user_string_group_list(user) for user in group.students]
    users_list = '\n'.join(user_list)

    group_string = group_string + users_list + '\n\n'

    return group_string


def get_student_list_as_file(client, activation_link=''):
    user_list = client.fetch_students()
    user_strings = [_formatted_user_string(get_user_with_activation(user, activation_link)) for user in user_list]

    return '\n'.join(user_strings)


def get_user_with_activation(user, activation_link):
    try:
        activation_record = UserActivation.get_user_activation(user)
        if activation_record:
            user.activation_link = "{}/{}".format(activation_link, activation_record.activation_key)
        else:
            user.activation_link = _('Activated')
    except:
        user.activation_link = _('Could not fetch activation record')

    return user


def get_group_list_as_file(group_projects, group_project_groups):
    user_ids = []
    for group_project in group_projects:
        for group in group_project_groups[group_project.id]:
            user_ids.extend([str(u.id) for u in group.users])
    additional_fields = ['first_name', 'last_name']
    user_dict = {str(u.id): u for u in user_api.get_users(ids=user_ids, fields=additional_fields)} if len(
        user_ids) > 0 else {}

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
    students = course_api.get_course_details_users(course.id,
                                                   {'page_size': 0, 'fields': 'id,email,username,organizations'})

    companies = {}
    students_dot = []
    for student in students:
        student_data = DottableDict({"id": student['id'], "email": student['email'], "username": student['username']})
        studentCompanies = student["organizations"]
        if len(studentCompanies) > 0:
            company = DottableDict(studentCompanies[0])
            if not company["id"] in companies:
                companies[company["id"]] = company
            student_data.company = companies[company["id"]]
        students_dot.append(student_data)
    return students_dot, companies


def parse_studentslist_from_post(postValues):
    students = []
    i = 0
    project_id = None
    try:
        project_id = postValues['project_id']
        while (postValues['students[{}]'.format(i)]):
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
        if value is not None:
            value = value.encode('ascii', 'ignore')
        """
        Fields that contain commas, quotes, and CR/LF need to be wrapped in double-quotes.
        If double-quotes are used to enclose fields, then a double-quote appearing inside a field must be escaped
        by preceding it with another double quote.
        """
        return '"{}"'.format(value.replace('"', '""')) if value is not None else ''

    def output_line(line_data_array):
        output_lines.append(','.join(line_data_array))

    activity_names_row = [_("Client Name"),"",_("Course ID"),""]
    output_line(activity_names_row)

    group_header_row = [client.name, "", course_id]
    output_line(group_header_row)

    output_line("--------")

    activity_names_row = [_("Full Name"),_("Username"),_("Title"),_("Email"), _("Progress %"), _("Engagement"), _("Proficiency"), _("Course Completed")]
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
    percent_completed = _('0%')
    if users_enrolled > 0:
        percent_completed = _("{}%").format(int((float(users_completed) / float(users_enrolled)) * 100))
    return users_completed, percent_completed


def get_course_metrics_for_organization(course_id, client_id):
    metrics = course_api.get_course_metrics(course_id, organization=client_id, metrics_required='users_started')
    org_metrics = organization_api.get_grade_complete_count(client_id, courses=course_id)
    metrics.users_grade_complete_count = org_metrics.users_grade_complete_count
    metrics.users_grade_average = org_metrics.users_grade_average
    metrics.percent_completed = 0
    if metrics.users_enrolled:
        metrics.percent_completed = int(float(metrics.users_grade_complete_count) / int(metrics.users_enrolled) * 100)
    return metrics


def get_course_analytics_progress_data(course, course_modules, client_id=None):
    params = {
        'page_size': 0,
        'fields': 'id,username',
    }
    if client_id:
        params.update({'organizations': client_id})
    user_list = course_api.get_course_details_users(course.id, params)
    users_count = len({u['id'] for u in user_list})
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
    metricsJson = [[0, 0]]
    day = 1
    mod_completed = 0
    for i, metric in enumerate(metrics.modules_completed):
        mod_completed += metrics.modules_completed[i][1]
        metricsJson.append([day, round((float(mod_completed) / total * 100), 2)])
        day += 1

    return metricsJson


def get_course_details_progress_data(course, course_modules, users, company_id):
    start_date = course.start
    end_date = datetime.now()
    if course.end is not None:
        if end_date > course.end:
            end_date = course.end
    delta = end_date - start_date
    if company_id:
        metrics = course_api.get_course_time_series_metrics(course.id, start_date, end_date, interval='days',
                                                            organization=company_id)
    else:
        metrics = course_api.get_course_time_series_metrics(course.id, start_date, end_date, interval='days')

    total = len(users) * len(course_modules)
    engaged_total = 0

    if company_id:
        course_metrics = course_api.get_course_details_completions_leaders(course.id, company_id)
    else:
        course_metrics = course_api.get_course_details_completions_leaders(course.id)

    course_leaders_ids = [leader['id'] for leader in course_metrics['leaders']]
    for course_user in users:
        if course_user in course_leaders_ids:
            engaged_total += 1

    engaged_total = engaged_total * len(course_modules)

    metricsJsonAll = [[0, 0]]
    metricsJsonEng = [[0, 0]]

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
    fields = ['phone', 'full_name', 'title', 'profile_image']

    for group in groups:
        if group.type == "contact_group":
            users = group_api.get_users_in_group(group.id)
            if len(users) > 0:
                user_ids = [str(user.id) for user in users]
                contacts.extend(user_api.get_users(fields=fields, ids=user_ids))

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
            admin_users = user_api.get_users(ids=ids, fields=additional_fields)

        users.extend(admin_users)

    else:
        org = next((org for org in organizations if org.id == org_id), None)
        if org:
            ids = [str(id) for id in org.users]
            users = user_api.get_users(ids=ids, fields=additional_fields)

    return users


def get_program_data_for_report(client_id, program_id=None):
    programs = Client.fetch(client_id).fetch_programs()

    if len(programs) > 0:
        program = next((p for p in programs if p.id == program_id), programs[0])
        program_courses = program.fetch_courses()
        courses = []
        for pc in program_courses:
            course = course_models.Course(dictionary={'id': pc.course_id, 'name': pc.display_name})
            courses.append(course)
    else:
        program = None
        courses = course_api.parse_course_list_json_object(organization_api.get_organizations_courses(client_id))

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

    if not any([user.is_mcka_admin, user.is_client_admin, user.is_internal_admin, user.is_mcka_subadmin]):
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


def get_ta_accessible_course_ids(ta_user):
    """
    Get ids of courses a TA can access
    """
    user_roles = user_api.get_user_roles(ta_user.id)

    return [
        role.course_id
        for role in user_roles
        if USER_ROLES.TA == role.role
        ]


def get_accessible_courses(user):
    """ Returns all available courses for the provided user """

    courses_list = []
    if user.is_mcka_admin or user.is_mcka_subadmin:
        courses_list = course_api.get_course_list()
    elif user.is_internal_admin:
        internal_ids = get_internal_courses_ids()
        if len(internal_ids) > 0:
            courses_list = course_api.get_course_list(internal_ids)
    else:
        course_id_list = []
        user_roles = user_api.get_user_roles(user.id)
        for role in user_roles:
            if USER_ROLES.TA == role.role:
                course_id_list.append(role.course_id)
        courses_list = course_api.get_course_list(course_id_list)

    return courses_list


def get_accessible_courses_from_program(user, program_id, restrict_to_courses_ids=None):
    program = Program.fetch(program_id)
    courses = program.fetch_courses()
    if not any([user.is_client_admin, user.is_mcka_admin, user.is_internal_admin, user.is_mcka_subadmin]):
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
            if companies.get(project.organization, None):
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
        client = client

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


def get_course_social_engagement(course_id, company_id):
    if company_id:
        course_users_simple = course_api.get_course_details_users(course_id, {'page_size': 0, 'fields': 'id',
                                                                              'organizations': company_id})
    else:
        course_users_simple = course_api.get_course_details_users(course_id, {'page_size': 0, 'fields': 'id'})
    course_users_ids = [str(user['id']) for user in course_users_simple]
    roles = course_api.get_users_filtered_by_role(course_id)
    roles_ids = [str(user.id) for user in roles]
    for role_id in roles_ids:
        if role_id in course_users_ids: course_users_ids.remove(role_id)

    number_of_users = len(course_users_ids)

    number_of_posts = 0
    number_of_participants_posting = 0
    if company_id:
        course_metrics_social = course_api.get_course_details_metrics_social(course_id, {'organization': company_id})
    else:
        course_metrics_social = course_api.get_course_details_metrics_social(course_id)

    for user in course_metrics_social['users']:
        if str(user) in course_users_ids:
            user_data = course_metrics_social['users'][str(user)]
            number_of_participants_posting += 1
            number_of_posts_per_participant = user_data['num_threads'] + user_data['num_replies'] + user_data[
                'num_comments']
            number_of_posts += number_of_posts_per_participant

    if number_of_users:
        participants_posting = str(
            round_to_int_bump_zero(float(number_of_participants_posting) * 100 / number_of_users)) + '%'
        avg_posts = round(float(number_of_posts) / number_of_users, 1)
    else:
        participants_posting = 0
        avg_posts = 0

    course_stats = [
        { 'name': _('# of posts'), 'value': number_of_posts},
        { 'name': _('% participants posting'), 'value': participants_posting},
        { 'name': _('Avg posts per participant'), 'value': avg_posts}
    ]

    return course_stats


def get_course_engagement_summary(course_id, company_id):
    params = {
        'page_size': 0,
        'fields': 'id,is_active,last_login',
    }
    if company_id:
        params.update({'organizations': company_id})
    course_users_simple = course_api.get_course_details_users(course_id, params)

    course_users_ids = [str(user['id']) for user in course_users_simple]
    roles = course_api.get_users_filtered_by_role(course_id)
    roles_ids = [str(user.id) for user in roles]
    for role_id in roles_ids:
        if role_id in course_users_ids: course_users_ids.remove(role_id)

    course_users = []
    for user in course_users_simple:
        if str(user['id']) in course_users_ids:
            course_users.append(user)

    if company_id:
        course_metrics = course_api.get_course_details_completions_leaders(course_id, company_id)
    else:
        course_metrics = course_api.get_course_details_completions_leaders(course_id)

    course_leaders_ids = [str(leader['id']) for leader in course_metrics['leaders']]

    active_users = 0
    login_users = 0
    login_users_progress = 0
    engaged_users = 0
    engaged_progress_sum = 0
    course_users_filtered_ids = [str(user['id']) for user in course_users]
    for leader in course_metrics['leaders']:
        if str(leader['id']) in course_users_filtered_ids:
            engaged_progress_sum += leader['completions']
    for course_user in course_users:
        if course_user['is_active'] is True:
            active_users += 1
        if course_user['last_login'] and \
                        parsedate(course_user['last_login']) >= (timezone.now() - timezone.timedelta(days=7)):
            login_users += 1
            for leader in course_metrics['leaders']:
                if leader['id'] == course_user['id']:
                    login_users_progress += leader['completions']
        if str(course_user['id']) in course_leaders_ids:
            engaged_users += 1

    course_progress = round_to_int_bump_zero(float(engaged_progress_sum) / len(course_users)) if len(
        course_users) > 0 else 0
    activated = round_to_int_bump_zero((float(active_users) / len(course_users)) * 100) if len(course_users) > 0 else 0
    engaged = round_to_int_bump_zero((float(engaged_users) / len(course_users)) * 100) if len(course_users) > 0 else 0
    active_progress = round_to_int_bump_zero(float(engaged_progress_sum) / active_users) if active_users > 0 else 0
    engaged_progress = round_to_int_bump_zero(float(engaged_progress_sum) / engaged_users) if engaged_users > 0 else 0
    logined_users = round_to_int_bump_zero((float(login_users) / len(course_users)) * 100) if len(
        course_users) > 0 else 0
    login_progress = round_to_int_bump_zero((float(login_users_progress) / login_users)) if login_users > 0 else 0

    course_stats = [
         { 'name': _('Total Cohort'), 'people': len(course_users), 'invited': '-', 'progress': str(course_progress) + '%'},
         { 'name': _('Activated'), 'people': active_users, 'invited': str(activated) + '%', 'progress': str(active_progress) + '%'},
         { 'name': _('Engaged'), 'people': engaged_users, 'invited': str(engaged) + '%', 'progress': str(engaged_progress) + '%'},
         { 'name': _('Logged in over last 7 days'), 'people': login_users, 'invited': str(logined_users) + '%', 'progress': str(login_progress) + '%'}
    ]

    return course_stats


def course_bulk_actions(course_id, data, batch_status, request):
    batch_status.clean_old()
    _thread = threading.Thread(target=_worker)  # one is enough; it's postponed after all
    _thread.daemon = True  # so we can exit
    _thread.start()
    course_bulk_action(course_id, data, batch_status, request)


@postpone
def course_bulk_action(course_id, data, batch_status, request):
    if (data['type'] == 'status_change'):
        if batch_status is not None:
            batch_status.attempted = len(data['list_of_items'])
            batch_status.save()
        for status_item in data['list_of_items']:
            status = change_user_status(course_id, data['new_status'], status_item)
            if (status['status'] == 'error'):
                if batch_status is not None:
                    batch_status.failed = batch_status.failed + 1
                    batch_status.save()
                    BatchOperationErrors.create(error=status["message"], task_key=batch_status.task_key,
                                                user_id=int(status_item['id']))
            elif (status['status'] == 'success'):
                if batch_status is not None:
                    batch_status.succeded = batch_status.succeded + 1
                    batch_status.save()
    elif (data['type'] == 'unenroll_participants'):
        if batch_status is not None:
            batch_status.attempted = len(data['list_of_items'])
            batch_status.save()
        for status_item in data['list_of_items']:
            status = unenroll_participant(course_id, status_item)
            if (status['status'] == 'error'):
                if batch_status is not None:
                    batch_status.failed = batch_status.failed + 1
                    batch_status.save()
                    BatchOperationErrors.create(error=status["message"], task_key=batch_status.task_key,
                                                user_id=int(status_item['id']))
            elif (status['status'] == 'success'):
                if batch_status is not None:
                    batch_status.succeded = batch_status.succeded + 1
                    batch_status.save()
    elif (data['type'] == 'enroll_participants'):
        if batch_status is not None:
            batch_status.attempted = len(data['list_of_items'])
            batch_status.save()
        for status_item in data['list_of_items']:
            status = _enroll_participant_with_status(data['course_id'], status_item['id'], data['new_status'])
            if (status['status'] == 'error'):
                if batch_status is not None:
                    batch_status.failed = batch_status.failed + 1
                    batch_status.save()
                    BatchOperationErrors.create(error=status["message"], task_key=batch_status.task_key,
                                                user_id=int(status_item['id']))
            elif (status['status'] == 'success'):
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
        return {'status': 'error', 'message': e.message}
    try:
        permissions = Permissions(user_id)
        if status != 'Active':
            permissions.update_course_role(course_id, permissonsMap[status])
    except ApiError as e:
        failure = {
            "status": 'error',
            "message": e.message
        }
    if failure:
        return {'status': 'error', 'message': e.message}

    return {'status': 'success'}


def unenroll_participant(course_id, user_id):
    try:
        permissions = Permissions(user_id)
        permissions.remove_all_course_roles(course_id)
        user_groups = user_api.get_user_workgroups(user_id, course_id)
        for group in user_groups:
            workgroup_api.remove_user_from_workgroup(vars(group)['id'], user_id)
        user_api.unenroll_user_from_course(user_id, course_id)
    except ApiError as e:
        return {'status': 'error', 'message': e.message}
    return {'status': 'success'}


def change_user_status(course_id, new_status, status_item):
    permissonsMap = {
        'TA': USER_ROLES.TA,
        'Observer': USER_ROLES.OBSERVER
    }
    try:
        permissions = Permissions(status_item['id'])
        permissions.update_course_role(course_id, permissonsMap.get(new_status, ""))
    except ApiError as e:
        return {'status': 'error', 'message': e.message}
    return {'status': 'success'}


def get_course_users_roles(course_id, permissions_filter_list):
    course_roles_users = course_api.get_users_filtered_by_role(course_id)
    user_roles_list = {'ids': [], 'data': []}
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


def get_user_courses_helper(user_id, request):
    user_courses = []
    allCourses = user_api.get_courses_from_user(user_id)

    for course in allCourses:
        user_course = {}
        user_course['name'] = course['name']
        user_course['id'] = course['id']
        user_course['program'] = '-'
        user_course['progress'] = "."
        user_course['proficiency'] = "."
        user_course['completed'] = 'N/A'
        user_course['grade'] = 'N/A'
        user_course['status'] = 'Participant'
        user_course['unenroll'] = 'Unenroll'
        user_course['start'] = course['start']
        if course['end'] is not None:
            user_course['end'] = course['end']
        else:
            user_course['end'] = _('-')
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
            user_course['completed'] = 'N/A'
            user_course['grade'] = 'N/A'
            user_course['status'] = 'Participant'
            user_course['start'] = course['start']
            if course['end'] is not None:
                user_course['end'] = course['end']
            else:
                user_course['end'] = '-'
            if vars(role)['role'] == 'observer':
                user_course['status'] = 'Observer'
            if vars(role)['role'] == 'assistant':
                user_course['status'] = 'TA'
            if vars(role)['role'] == 'staff':
                user_course['status'] = 'Staff'
            if vars(role)['role'] == 'instructor':
                user_course['status'] = 'Instructor'
            user_course['unenroll'] = 'Unenroll'
            user_courses.append(user_course)
        else:
            user_course = (user_course for user_course in user_courses if
                           user_course["id"] == vars(role)['course_id']).next()
            if user_course['status'] != 'TA':
                if vars(role)['role'] == 'observer':
                    user_course['status'] = 'Observer'
                if vars(role)['role'] == 'assistant':
                    user_course['status'] = 'TA'
                if vars(role)['role'] == 'staff':
                    user_course['status'] = 'Staff'
                if vars(role)['role'] == 'instructor':
                    user_course['status'] = 'Instructor'

    if request.user.is_internal_admin:
        internal_ids = get_internal_courses_ids()
        user_courses = [course for course in user_courses if course['id'] in internal_ids]

    # xss cleaning of course properties
    for course in user_courses:
        sanitize_data(
            data=course, props_to_clean=settings.COURSE_PROPERTIES_TO_CLEAN,
            clean_methods=(clean_xss_characters,)
        )

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


def import_participants_threaded(student_list, request, reg_status):
    _thread = threading.Thread(target=_worker)  # one is enough; it's postponed after all
    _thread.daemon = True  # so we can exit
    _thread.start()
    process_import_participants_list(student_list, request, reg_status)


def enroll_participants_threaded(student_list, request, reg_status):
    _thread = threading.Thread(target=_worker)  # one is enough; it's postponed after all
    _thread.daemon = True  # so we can exit
    _thread.start()
    process_enroll_participants_list(student_list, request, reg_status)


@postpone
def process_import_participants_list(file_stream, request, reg_status=None):
    # 1) Build user list
    user_list = build_student_list_from_file(file_stream, parse_method=_process_line_register_participants_csv)
    if reg_status is not None:
        reg_status.attempted = len(user_list)
        reg_status.save()
    for user_info in user_list:
        if "error" in user_info:
            error = UserRegistrationError.create(error=user_info["error"], task_key=reg_status.task_key)
            reg_status.failed = reg_status.failed + 1
            reg_status.save()
    user_list = [user_info for user_info in user_list if "error" not in user_info]
    # 2) Register the users, and associate them with client
    _enroll_participants(user_list, request, reg_status)


@postpone
def process_enroll_participants_list(file_stream, request, reg_status=None):
    # 1) Build user list
    user_list = build_student_list_from_file(file_stream, parse_method=_process_line_enroll_participants_csv)
    if reg_status is not None:
        reg_status.attempted = len(user_list)
        reg_status.save()
    for user_info in user_list:
        if "error" in user_info:
            error = UserRegistrationError.create(error=user_info["error"], task_key=reg_status.task_key)
            reg_status.failed = reg_status.failed + 1
            reg_status.save()
    user_list = [user_info for user_info in user_list if "error" not in user_info]
    # 2) enroll the users
    _just_enroll_participants(user_list, request, reg_status)


def _process_line_register_participants_csv(user_line):
    try:
        fields = user_line.strip().split(',')
        # format is FirstName, LastName, Email, Company, CourseID, Status

        first_name = normalize_foreign_characters(remove_characters(fields[0], ["'"]).encode("utf-8"))
        last_name = normalize_foreign_characters(remove_characters(fields[1], ["'"]).encode("utf-8"))
        email = normalize_foreign_characters(fields[2])

        # temporarily set the user name to the first 30 characters of the allowed characters within the email
        username = re.sub(r'\W', '', fields[2])
        if len(username) > 30:
            username = username[:29]

        validate_first_name(first_name)
        validate_last_name(last_name)
        validate_email(email)

        user_info = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "company_id": fields[3],
            "course_id": fields[4],
            "status": fields[5],
            "username": username,
            "is_active": False,
            "password": settings.INITIAL_PASSWORD,
        }
    except ValidationError as e:
        user_info = {'error': ("{} Participant {}".format(e.message, fields[2]))}
    except Exception as e:
        user_info = {
            "error": _("Could not parse user info from {}").format(fields[2])
        }

    return user_info


def _process_line_enroll_participants_csv(user_line):
    try:
        fields = user_line.strip().split(',')
        # format is Email, CourseID, Status

        user_info = {
            "email": fields[0],
            "course_id": fields[1],
            "status": fields[2]
        }

    except Exception as e:
        user_info = {
            "error": _("Could not parse user info from {}").format(user_line)
        }

    return user_info


def _enroll_participants(participants, request, reg_status):
    permissonsMap = {
        'ta': USER_ROLES.TA,
        'observer': USER_ROLES.OBSERVER
    }

    internalAdminFlag = False
    if request.user.is_internal_admin:
        internalAdminFlag = True

    for user_dict in participants:

        user = None
        client = None
        course = None
        username = user_dict['username']
        client_id = user_dict['company_id']
        course_id = user_dict['course_id']
        status = user_dict['status'].lower()
        status_check = ['participant', 'observer', 'ta']
        check_errors = []
        user_error = []
        user_email = user_dict.get('email', '')
        email = user_dict.get('email', '')

        try:
            # Check for empty fields
            for key, value in user_dict.items():
                if str(value).strip() == '':
                    if key == 'email':
                        email = _("No email")
                    if key != 'username':
                        check_errors.append({'reason': _('Empty field: {}').format(key), 'activity': _('Processing Participant')})
            #Check if email is valid
            try:
                validate_email(user_email)
            except ValidationError:
                check_errors.append({'reason': _('Valid e-mail is required'), 'activity': _('Registering Participant')})
            else:
                # run through API only if valid email is given as API breaks on wrong email

                # Check if email already exist
                check_user_email = user_api.get_user_by_email(user_email)
                if check_user_email['count'] == 1:
                    check_errors.append({'reason': _('Email already exist'), 'activity': _('Registering Participant')})
                else:
                    # Check if username already exist
                    check_user_username = user_api.get_user_by_username(username)
                    if check_user_username['count'] == 1:
                        check_errors.append({'reason': _('Username already exist'), 'activity': _('Registering Participant')})
            #Check if client exist
            try:
                client = Client.fetch(client_id)
            except ApiError as e:
                if e.message == 'NOT FOUND':
                    check_errors.append({'reason': _("Company doesn't exist"), 'activity': _('Enrolling Participant in Company')})
                else:
                    check_errors.append({'reason': '{}'.format(e.message), 'activity': _('Enrolling Participant in Company')})
            #Check if course exist
            try:
                course = course_api.get_course_details(course_id)
            except ApiError as e:
                if e.message == 'NOT FOUND':
                    check_errors.append({'reason': _("Course doesn't exist"), 'activity': _('Enrolling Participant in Course')})
                else:
                    check_errors.append({'reason': '{}'.format(e.message), 'activity': _('Enrolling Participant in Course')})
            #For Internal Admin Check if Course Is Internal
            if internalAdminFlag:
                if not check_if_course_is_internal(course_id):
                    check_errors.append({'reason': _("Course is not Internal"), 'activity': _('Enrolling Participant in Course')})
            #Check if status exist
            if status not in status_check:
                check_errors.append({'reason': _("Status doesn't exist"), 'activity': _('Enrolling Participant in Course')})
            #If errors exist add them, else continue
            if check_errors:
                for error in check_errors:
                    user_error.append(_("Reason: {}, Activity: {}, Participant: {}").format(
                        error['reason'],
                        error['activity'],
                        email
                    ))
            else:
                try:
                    # Register Participant
                    try:
                        user = user_api.register_user(user_dict)
                    except ApiError as e:
                        raise ValueError('{}'.format(e.message), _('Registering Participant'))
                    #Enroll Participant in Client
                    try:
                        client.add_user(user.id)
                    except ApiError as e:
                        raise ValueError('{}'.format(e.message), _('Enrolling Participant in Company'))
                    #Create Activation Record for Participant
                    if not user.is_active:
                        activation_record = UserActivation.user_activation_by_task_key(user, reg_status.task_key,
                                                                                       client_id)
                    if not activation_record:
                        raise ValueError(_('Activation record error'), _('Registering Participant'))
                    #Enroll Participant in Course
                    try:
                        user_api.enroll_user_in_course(user.id, course_id)
                    except ApiError as e:
                        raise ValueError('{}'.format(e.message), _('Enrolling Participant in Course'))
                    #Set Participant Status on Course
                    try:
                        permissions = SlimAddingPermissions(user.id)
                        if status != 'participant':
                            permissions.add_course_role(course_id, permissonsMap[status])
                    except ApiError as e:
                        raise ValueError('{}'.format(e.message), _("Setting Participant's Status"))
                except ValueError as e:
                    user_error.append(_("Reason: {}, Activity: {}, Participant: {}").format(
                        e.args[0],
                        e.args[1],
                        email
                    ))
        except Exception as e:
            reason = e.message if e.message else _("Processing Data Error")
            user_error.append(_("Error processing data: {} - {}").format(
                reason,
                email
            ))

        if user_error:
            for user_e in user_error:
                error = UserRegistrationError.create(error=user_e, task_key=reg_status.task_key)
            reg_status.failed = reg_status.failed + 1
            reg_status.save()
        else:
            reg_status.succeded = reg_status.succeded + 1
            reg_status.save()


def _just_enroll_participants(participants, request, reg_status):
    permissonsMap = {
        'ta': USER_ROLES.TA,
        'observer': USER_ROLES.OBSERVER
    }

    internalAdminFlag = False
    if request.user.is_internal_admin:
        internalAdminFlag = True

    for user_dict in participants:

        course_id = user_dict['course_id'].strip()
        status = user_dict['status'].lower().strip()
        status_check = ['participant', 'observer', 'ta']
        check_errors = []
        user_error = []
        user_email = user_dict.get('email', '').strip()
        email = user_dict.get('email', '').strip()
        try:
            # Check for empty fields
            for key, value in user_dict.items():
                if str(value).strip() == '':
                    if key == 'email':
                        email = _("No email")
                    check_errors.append({'reason': _('Empty field: {}').format(key), 'activity': _('Processing Participant')})
            #Check if email is valid
            try:
                validate_email(user_email)
            except ValidationError:
                check_errors.append({'reason': _('Valid e-mail is required: {email}').format(user_email), 'activity': _('Processing Participant')})
            #Check if user already exist
            user_data = user_api.get_user_by_email(user_email)
            if user_data['count'] == 0:
                check_errors.append({'reason': _("User doesn't exist"), 'activity': _('Processing Participant')})
            #Check if course exist
            try:
                course = course_api.get_course_details(course_id)
            except ApiError as e:
                if e.message == 'NOT FOUND':
                    check_errors.append({'reason': _("Course doesn't exist"), 'activity': _('Enrolling Participant in Course')})
                else:
                    check_errors.append({'reason': '{}'.format(e.message), 'activity': _('Enrolling Participant in Course')})
            #For Internal Admin Check if Course Is Internal
            if internalAdminFlag:
                if not check_if_course_is_internal(course_id):
                    check_errors.append({'reason': _("Course is not Internal"), 'activity': _('Enrolling Participant in Course')})
            #Check if status exist
            if status not in status_check:
                check_errors.append({'reason': _("Status doesn't exist"), 'activity': _('Enrolling Participant in Course')})
            #If errors exist add them, else continue
            if check_errors:
                for error in check_errors:
                    user_error.append(_("Reason: {}, Activity: {}, Participant: {}").format(
                        error['reason'],
                        error['activity'],
                        email
                    ))
            else:
                try:
                    # Enroll Participant in Course
                    try:
                        user_api.enroll_user_in_course(user_data["results"][0]["id"], course_id)
                    except ApiError as e:
                        raise ValueError('{}'.format(e.message), _('Enrolling Participant in Course'))
                    #Set Participant Status on Course
                    try:
                        permissions = Permissions(user_data["results"][0]["id"])
                        if status != 'participant':
                            permissions.add_course_role(course_id, permissonsMap[status])
                    except ApiError as e:
                        raise ValueError('{}'.format(e.message), _("Setting Participant's Status"))
                except ValueError as e:
                    user_error.append(_("Reason: {}, Activity: {}, Participant: {}").format(
                        e.args[0],
                        e.args[1],
                        email
                    ))
        except Exception as e:
            reason = e.message if e.message else _("Processing Data Error")
            user_error.append(_("Error processing data: {} - {}").format(
                reason,
                email
            ))

        if user_error:
            for user_e in user_error:
                error = UserRegistrationError.create(error=user_e, task_key=reg_status.task_key)
            reg_status.failed = reg_status.failed + 1
            reg_status.save()
        else:
            reg_status.succeded = reg_status.succeded + 1
            reg_status.save()


def _send_activation_email_to_single_new_user(activation_record, user, absolute_uri):
    msg = [email_add_single_new_user(absolute_uri, user, activation_record)]
    result = sendMultipleEmails(msg)
    return result


def _send_multiple_emails(from_email=None, to_email_list=None, subject=None, email_body=None, template_id=None,
                          optional_data=None):
    if template_id:
        template = EmailTemplate.objects.get(pk=template_id)
        subject = template.subject
        email_body = template.body

    if optional_data:
        msg = []
        parsed_emails = _parse_email_text_template(email_body, optional_data)
        if parsed_emails["parsable"]:
            for email_data in parsed_emails["proccessed_email_data"]:
                msg.append(create_multiple_emails(from_email, [email_data["email"]], subject, email_data["email_body"]))
        else:
            msg = [create_multiple_emails(from_email, to_email_list, subject, email_body)]

    else:
        msg = [create_multiple_emails(from_email, to_email_list, subject, email_body)]
    result = sendMultipleEmails(msg)
    return result


def _parse_email_text_template(text_body, optional_data=None):
    parsed = {"parsable": False}
    parsed["proccessed_email_data"] = []
    if text_body and optional_data:
        list_of_keywords = ["FIRST_NAME", "LAST_NAME", "PROGRESS", "PROFICIENCY", "SOCIAL_ENGAGEMENT", "COMPANY"]
        list_of_found = [False, False, False, False, False, False]
        set_of_delimiter = [["&lt;&lt;", "&gt;&gt;"], ["<<", ">>"]]
        use_delimiter = 0
        for keyword in list_of_keywords:
            for delimiter in set_of_delimiter:
                delimiter_construct = delimiter[0] + "{}" + delimiter[1]
                if text_body.find(delimiter_construct.format(keyword)) > -1:
                    parsed["parsable"] = True
                    list_of_found[list_of_keywords.index(keyword)] = True
                    use_delimiter = set_of_delimiter.index(delimiter)
        if parsed["parsable"]:
            delimiter = set_of_delimiter[use_delimiter]
            delimiter_construct = delimiter[0] + "{}" + delimiter[1]
            temp_text_parsed = text_body
            for keyword in list_of_keywords:
                temp_text_parsed = temp_text_parsed.replace(delimiter_construct.format(keyword),
                                                            "{{" + keyword.lower() + "}}")
            string_template = CustomTemplate(temp_text_parsed)
            for user in optional_data.get("user_list", []):
                temp_text = text_body
                constructed_vars = {}
                for keyword in list_of_keywords:
                    if list_of_found[list_of_keywords.index(keyword)]:
                        if keyword == "FIRST_NAME":
                            constructed_vars[keyword.lower()] = user["first_name"]
                        elif keyword == "LAST_NAME":
                            constructed_vars[keyword.lower()] = user["last_name"]
                        elif keyword == "PROGRESS":
                            constructed_vars[keyword.lower()] = str(int(user.get("progress", 0))) + "%"
                        elif keyword == "PROFICIENCY":
                            constructed_vars[keyword.lower()] = str(int(user.get("proficiency", 0))) + "%"
                        elif keyword == "SOCIAL_ENGAGEMENT":
                            social_engagement_data = user_api.get_course_social_metrics(user["id"],
                                                                                        optional_data["course_id"])
                            if social_engagement_data:
                                constructed_vars[keyword.lower()] = "threads: {}, comments: {}, replies: {}".format(social_engagement_data.num_threads,
                                    social_engagement_data.num_comments, social_engagement_data.num_replies)
                        elif keyword == "COMPANY":
                            constructed_vars[keyword.lower()] = user["organization_name"]
                temp_text = string_template.safe_substitute(constructed_vars)
                parsed["proccessed_email_data"].append({"email_body": temp_text, "email": user["email"]})
        return parsed


def send_activation_emails_by_task_key(request, task_key):
    absolute_uri = request.build_absolute_uri('/accounts/activate')
    activation_records = UserActivation.get_activations_by_task_key(task_key=task_key)

    for record in activation_records:
        _send_activation_email_to_single_new_user(record, record, absolute_uri)


def get_company_active_courses(company_courses):
    active_courses = []
    for company_course in company_courses:
        if timezone.now() >= (company_course['start']):
            if company_course['end'] is None or '-':
                active_courses.append(company_course)
            elif timezone.now() <= (company_course['end']):
                active_courses.append(company_course)

    return active_courses


def validate_company_display_name(company_display_name):
    company = organization_api.get_organization_by_display_name(urllib.quote_plus(company_display_name))
    if company['count'] != 0:
        return {'status': 'error', 'message': _('This company already exists!')}

    return {'status': 'ok', 'message': _('Company Validation Success!')}


def get_internal_courses_ids():
    """ Return a List of internal courses Id's """
    internal_ids = []
    internal_courses = get_internal_courses_list()
    for course in internal_courses:
        internal_ids.append(vars(course)['course_id'])
    return internal_ids


def get_internal_courses_list():
    """ Return a List of courses tagged :internal """
    internal_tags = group_api.get_groups_of_type(group_type=TAG_GROUPS.INTERNAL)
    internal_courses = []
    for internal_tag in internal_tags:
        internal_courses.extend(group_api.get_courses_in_group(group_id=vars(internal_tag)['id']))

    return internal_courses


def check_if_course_is_internal(course_id):
    internal_ids = get_internal_courses_ids()
    if str(course_id) in internal_ids:
        return True
    return False


def check_if_user_is_internal(user_id):
    user_courses = user_api.get_courses_from_user(user_id)
    internal_ids = get_internal_courses_ids()
    for course in user_courses:
        if course['id'] in internal_ids:
            return True
    return False


class CustomTemplate(string.Template):
    delimiter = '{{'
    pattern = r'''
    \{\{(?:
    (?P<escaped>\{\{)|
    (?P<named>[_a-z][_a-z0-9]*)\}\}|
    (?P<braced>[_a-z][_a-z0-9]*)\}\}|
    (?P<invalid>)
    )'''


def student_list_chunks_tracker(data, client_id, activation_link):
    default_chunk_size = 100
    respone_data = {}

    if data.get("task_id", None):
        cached_student_progress = cache.get('student-list-' + data["task_id"], None)

        if cached_student_progress:
            chunk_count = int(cached_student_progress.get("chunk_count", 0))
            chunk_request = int(data.get("chunk_request", 0))

            if chunk_request < chunk_count:
                chunks = cached_student_progress.get("list_chunked", [])
                users_ids = [str(user_id) for user_id in chunks[chunk_request]]
                if users_ids == []:
                    user_list = []
                else:
                    additional_fields = ["title", "city", "country", "first_name", "last_name"]
                    user_list = user_api.get_users(ids=users_ids, fields=additional_fields)
                user_strings = [_formatted_user_array(get_user_with_activation(user, activation_link)) for user in
                                user_list]
                return {"task_id": data["task_id"], "chunk_count": chunk_count, "chunk_request": chunk_request + 1,
                        "chunk_size": cached_student_progress.get("chunk_size", default_chunk_size),
                        "file_name": cached_student_progress.get("file_name", "download.csv"),
                        "element_count": cached_student_progress.get("element_count", 0), "data": user_strings,
                        "status": "csv_chunk_sent"}
            else:
                return {"status": "error", "message": _("You have sent incorrect chunk number!")}
        else:
            return {"status": "error", "message": _("You have sent incorrect task key!")}
    else:
        unique_id = str(uuid.uuid4());
        cached_data = {}
        user_list = organization_api.fetch_organization_user_ids(client_id)
        user_list_chunked = None
        chunk_size = int(data.get("chunk_size", default_chunk_size))

        if len(user_list):

            client = Client.fetch(client_id)
            file_name = unicode("Student List for {} on {}.csv".format(client.display_name, datetime.now().isoformat()))

            user_list_chunked = [user_list[i:i + chunk_size] for i in xrange(0, len(user_list), chunk_size)]
            cached_data["chunk_count"] = len(user_list_chunked);
            cached_data["list_chunked"] = user_list_chunked
            cached_data["element_count"] = len(user_list)
            cached_data["chunk_size"] = chunk_size
            cached_data["file_name"] = file_name
            cache.set('student-list-' + unique_id, cached_data)
        else:
            return {"status": "error", "message": _("There are no users in organization!")}

        return {"task_id": unique_id, "chunk_count": cached_data["chunk_count"], "chunk_size": chunk_size,
                "element_count": len(user_list), "status": "csv_task_created",
                "file_name": file_name}


def construct_users_list(enrolled_users, registration_requests):
    '''
    Returns users list of dictionaries with activation and enrollment status
    '''

    def check_user_status(registration_request):
        for user in enrolled_users:
            if user['email'] == registration_request.company_email:
                return True, user['is_active']
        return False, False

    full_users_list = []
    full_user_row = {}

    for registration_request in registration_requests:
        enrolled, activated = check_user_status(registration_request)
        full_user_row['id'] = registration_request.pk
        full_user_row['first_name'] = registration_request.first_name
        full_user_row['last_name'] = registration_request.last_name
        full_user_row['is_active'] = activated
        full_user_row['is_enrolled'] = enrolled
        full_user_row['company_name'] = registration_request.company_name
        full_user_row['company_email'] = registration_request.company_email
        full_user_row['current_role'] = registration_request.current_role
        full_user_row['mcka_user'] = registration_request.mcka_user
        full_user_row['new_user'] = registration_request.new_user
        full_users_list.append(full_user_row)
        full_user_row = {}

    return full_users_list


class CourseParticipantStats(object):
    """
    Utility for handling stats retrieval of course participants
    """
    permission_map = {
        'assistant': 'TA',
        'instructor': 'Instructor',
        'staff': 'Staff',
        'observer': 'Observer'
    }

    def __init__(self, course_id, base_url, record_parser=None, restrict_to_participants=None):
        self._additional_fields = None
        self.course_id = course_id
        self.base_url = base_url
        self.request_params = {}
        self.record_parser = record_parser
        self.participants_engagement_lookup = None
        self.restrict_to_participants = None
        if restrict_to_participants is not None:
            self.restrict_to_participants = {participant.username for participant in restrict_to_participants}

    def get_participants_data(self, request_params):
        """
        Public method for retrieving participants data
        based on `request_params`
        """
        self.request_params = request_params
        (
            course_participants,
            lesson_completions,
            participants_engagement_lookup,
            course_completions,
        ) = self._retrieve_api_data()

        return self._process_results(
            course_participants,
            course_completions,
            lesson_completions,
            participants_engagement_lookup,
        )

    @property
    def additional_fields(self):
        return self.request_params.get('additional_fields', '').split(',')

    def _retrieve_api_data(self):
        """
        Calls course api to get the stats
        """
        course_participants = course_api.get_course_details_users(self.course_id, self.request_params)

        if self.restrict_to_participants is not None:
            course_participants = filter_course_participants(course_participants, self.restrict_to_participants)

        organization_id = self.request_params.get('organizations', None)
        if organization_id:
            course_participants = remove_specific_user_roles_of_other_companies(course_participants, int(organization_id))

        lesson_completions = self._get_lesson_completions(course_participants)

        if self.participants_engagement_lookup is None:
            self.participants_engagement_lookup = self._get_engagement_scores()

        course_completions = course_api.get_course_completions(self.course_id, extra_fields=None)
        return (
            course_participants,
            lesson_completions,
            self.participants_engagement_lookup,
            course_completions,
        )

    def _get_engagement_scores(self):
        """
        Returns engagement score for all participants in the course.
        """
        course_social_metrics = course_api.get_course_social_metrics(self.course_id)
        participants_engagement_lookup = {}
        users_social_metrics = vars(course_social_metrics.users)
        for u_id, user_metrics in users_social_metrics.iteritems():
            engagement_score = 0
            for metric, metric_points in settings.SOCIAL_METRIC_POINTS.iteritems():
                engagement_score += getattr(user_metrics, metric, 0) * metric_points
            participants_engagement_lookup[str(u_id)] = engagement_score

        return participants_engagement_lookup

    def _get_lesson_completions(self, course_participants):
        """
        Returns completion data for all participants in the course.
        """
        if 'lesson_completions' not in self.additional_fields:
            return None
        oauth2_session = oauth2_requests.get_oauth2_session()
        lesson_completions = {}
        completions = course_api.get_course_completions(
            self.course_id,
            extra_fields='chapter',
            edx_oauth2_session=oauth2_session,
        )
        for user in course_participants['results']:
            lesson_completions[user['id']] = completions.get(user['username'])
        return lesson_completions

    def _get_lesson_mapping(self, user):
        """
        Return a mapping of lesson ids to numbers
        """
        course = _load_course(self.course_id, user=user)
        lesson_mapping = {}
        for idx, chapter in enumerate(course.chapters):
            lesson_mapping[chapter.id] = idx + 1
        return lesson_mapping

    def _get_normal_user(self, participants):
        """
        Return an enrolled user with no special role, if one exists in the course.

        Otherwise return any enrolled user.  If there are no enrolled users,
        return None.
        """
        users = participants['results']
        for user in users:
            if not user['roles']:
                return user

        if users:
            return users[0]

    def _process_results(
            self,
            participants,
            course_completions,
            lesson_completions=None,
            participants_engagement_lookup=None,
    ):
        """
        Integrates and process results set
        """
        participants_activation_links = self._participants_activation_urls(participants)

        for course_participant in participants['results']:
            # add in user activation link
            course_participant['activation_link'] = participants_activation_links.get(course_participant['id'], '')

            # transform to complete country name
            if course_participant.get('country'):
                course_participant['country'] = get_complete_country_name(course_participant.get('country'))

            if not course_participant.get('organizations'):
                course_participant['organizations'] = [{'display_name': _('No company')}]
                course_participant['organizations_display_name'] = _('No company')
            else:
                course_participant['organizations_display_name'] = course_participant['organizations'][0][
                    'display_name']
            if course_participant.get('roles'):
                if 'assistant' in course_participant['roles']:
                    course_participant['custom_user_status'] = self.permission_map['assistant']
                elif 'observer' in course_participant['roles']:
                    course_participant['custom_user_status'] = self.permission_map['observer']
                elif 'staff' in course_participant['roles']:
                    course_participant['custom_user_status'] = self.permission_map['staff']
                elif 'instructor' in course_participant['roles']:
                    course_participant['custom_user_status'] = self.permission_map['instructor']
            else:
                course_participant['custom_user_status'] = 'Participant'

            if course_participant['is_active']:
                course_participant['custom_activated'] = _('Yes')
            else:
                course_participant['custom_activated'] = _('No')

            if 'last_login' in course_participant:
                if (course_participant['last_login'] is not None) and (course_participant['last_login'] is not ''):
                    last_login = parsedate(course_participant['last_login'])
                    course_participant['custom_last_login'] = last_login.strftime(
                        "%Y/%m/%d") + ',' + last_login.strftime(
                        "%m/%d/%Y")
                else:
                    course_participant['custom_last_login'] = '-'
            else:
                course_participant['custom_last_login'] = '-'
            completion_data = course_completions.get(
                course_participant['username'], {}
            ).get('completion')
            if completion_data:
                percent = completion_data.get('percent') or 0.
                progress = round_to_int(percent * 100)
                course_participant['progress'] = '{:03d}'.format(progress)
            else:
                course_participant['progress'] = _("000")

            course_participant['engagement'] = participants_engagement_lookup.get(str(course_participant['id']), 0)

            if course_participant.get('grades', {}).get('grade'):
                proficiency = round_to_int(course_participant['grades']['grade'] * 100)
                course_participant['proficiency'] = '{:03d}'.format(proficiency)
            else:
                course_participant['proficiency'] = _("000")

            course_participant['number_of_assessments'] = 0
            course_participant['number_of_groupworks'] = 0
            course_participant['groupworks'] = []
            course_participant['assessments'] = []
            if participants['count']:
                if course_participant.get('grades', {}).get('section_breakdown'):
                    for user_grade in course_participant['grades']['section_breakdown']:
                        data = user_grade
                        data['percent'] = '{:03d}'.format(round_to_int(float(user_grade['percent']) * 100))
                        if 'assessment' in user_grade['category'].lower():
                            course_participant['number_of_assessments'] += 1
                            course_participant['assessments'].append(data)
                        if 'group_project' in user_grade['category'].lower():
                            course_participant['number_of_groupworks'] += 1

                            course_participant['groupworks'].append(data)

            # if a record parser is supplied, pass record through it
            if self.record_parser:
                self.record_parser(course_participant)
            if lesson_completions is not None:
                lesson_mapping = self._get_lesson_mapping(self._get_normal_user(participants))
                course_participant['lesson_completions'] = {}
                lesson_completion = lesson_completions.get(course_participant['id'], None)
                if lesson_completion:
                    del lesson_completion['completion']  # get rid of the course-level completion
                    for lesson in lesson_completion.values():
                        completion_percentage = round_to_int(
                            float(lesson['completion']['percent'] or 0.) * 100
                        )
                        block_key = lesson['block_key']
                        if block_key in lesson_mapping:
                            lesson_number = lesson_mapping[block_key]
                            course_participant['lesson_completions'][lesson_number] = completion_percentage
        return participants

    def _participants_activation_urls(self, participants_data):
        """
        Gets activation urls for participants records
        """
        user_ids = [result.get('id') for result in participants_data['results'] if not result['is_active']]

        return get_user_activation_links(
            user_ids, base_url=self.base_url
        )

    @staticmethod
    def participant_record_parser(participant_data):
        """
        additional parsing/transforming of participant data
        """
        last_login = participant_data['custom_last_login']
        if last_login != '-':
            try:
                last_login = last_login.split(',')[1]
            except IndexError:
                last_login = last_login[0]

        participant_data.update({
            'proficiency': '{}%'.format(participant_data.get('proficiency')),
            'progress': '{}%'.format(participant_data.get('progress')),
            'custom_last_login': last_login
        })


def filter_course_participants(course_participants, limit_participants):
    """
    Returns only those course participants also found in the limited list of participants.
    """
    updates = {
        'results': [
            participant for participant in course_participants.get('results', [])
                if participant.get('username') in limit_participants
        ]
    }
    updates['count'] = len(updates['results'])
    return dict(course_participants, **updates)


def remove_specific_user_roles_of_other_companies(course_participants, organization_id):
    """
    Returns course_participants with out users who are uber admin of one company
    and enrolled in other company course as company admin and observer or company
    admin and assidtant role.
    """
    remove_permissions = ['assistant', 'observer']
    users = []

    for user in course_participants["results"]:
        if user["organizations"][0]["id"] != organization_id:
            for role in user["roles"]:
                if role in remove_permissions:
                    users.append(user)

    for user in users:
        course_participants["results"].remove(user)

    return course_participants


def participant_csv_line_id_extractor(user_line):
    """
    Returns user id from the csv record of particpants
    assuming it's in first cell
    """
    fields = user_line.strip().split(',')

    if fields:
        try:
            user_id = int(fields[0])
        except ValueError:
            pass
        else:
            return user_id


def crop_image(request, img_name):
    """
    Crop the given image using parameters from request
    """
    left = int(float(request.POST.get('x1-position')))
    top = int(float(request.POST.get('y1-position')))
    right = int(float(request.POST.get('width-position'))) + left
    bottom = int(float(request.POST.get('height-position'))) + top
    image = Image.open(img_name)
    cropped_image = image.crop((left, top, right, bottom))
    image_io = StringIO.StringIO()
    cropped_image.convert('RGBA').save(image_io, format='PNG')
    image_io.seek(0)

    return image_io


def remove_desktop_branding_image(img_type, client_id):
    '''Removes the global, desktop logo and Background image '''
    customization = ClientCustomization.objects.get(client_id=client_id)
    image_url = getattr(customization, img_type).replace('/accounts/', '')
    if image_url and default_storage.exists(image_url):
        default_storage.delete(image_url)
    setattr(customization, img_type, '')
    customization.save()


def upload_mobile_branding_image(request, client_id):
    """
    uploads mobile app logo or mobile header background image which depends on
    request to platform
    """
    if 'mobile_app_logo' in request.FILES:
        image_io = crop_image(request, request.FILES['mobile_app_logo'])
        image_file = {'logo_image': ('logo.png', image_io, 'image/png')}
    else:
        image_io = crop_image(request, request.FILES['mobile_app_header_background'])
        image_file = {'header_bg_image': ('header_backgroung.png', image_io, 'image/png')}

    mobile_app_themes = get_mobile_app_themes(client_id)

    if mobile_app_themes:
        update_mobile_app_theme(
            mobile_app_themes[0]['id'],
            {'organization': client_id, 'active': True},
            image_file
        )
    else:
        create_mobile_app_theme(client_id, {'active': True}, image_file)


def update_mobile_client_detail_customization(request, client_id):
    """
    Update mobile clients theme attributes
    """
    mobile_branding_form = MobileBrandingForm(request.POST)

    if mobile_branding_form.is_valid():

        mobile_branding_data = mobile_branding_form.cleaned_data
        mobile_branding_data['organization'] = client_id
        mobile_branding_data['active'] = True
        mobile_app_themes = get_mobile_app_themes(client_id)
        if mobile_app_themes:
            update_mobile_app_theme(mobile_app_themes[0]['id'], mobile_branding_data)
        else:
            create_mobile_app_theme(client_id, mobile_branding_data)
        return None
    else:
        errors = str(mobile_branding_form.errors)
        cleantext = BeautifulSoup(errors, "html").text
        return cleantext


def create_roles_list(request):
    """It raises validation exception for values that starts with 'role' and doesn't
    validate the regex given in the RoleTitleValidator """
    role_validator = RoleTitleValidator()
    roles = []
    for key, value in request.POST.items()[::-1]:
        if key.startswith('role'):
            role_validator(value)
            roles.append(value)
    return roles


def edit_self_register_role(role_id, role_text):

    try:
        self_reg_role = SelfRegistrationRoles.objects.get(id=int(role_id))
    except ObjectDoesNotExist:
        return Response({'status': status.HTTP_404_NOT_FOUND, 'message': _('Sorry, We can not process your request')})

    if role_text:

        self_reg_role.option_text = role_text
        self_reg_role.save()

        return Response({'status': status.HTTP_200_OK, 'message': _('Operation Successful')})
    else:

        return Response({'status': status.HTTP_404_NOT_FOUND, 'message': _('Please enter role text')})


def delete_self_reg_role(role_id):

    try:
        self_reg_role = SelfRegistrationRoles.objects.get(id=int(role_id))
        self_reg_role.delete()

        return Response({'status': status.HTTP_200_OK, 'message': _('Operation Successful')})
    except ObjectDoesNotExist:

        return Response({'status': status.HTTP_404_NOT_FOUND, 'message': _('Sorry, We can not process your request')})

def get_course_stats_report(company_id, course_id):
    """ returns course stats in csv format inside http response """
    course = course_api.get_course_details(course_id)
    course_name = course['name'].replace(' ', '_')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + course_name + '_stats.csv"'

    writer = csv.writer(response)
    write_engagement_summary_on_csv(writer, course_id, company_id)
    write_participant_performance_on_csv(writer)

    (course_features, created) = FeatureFlags.objects.get_or_create(course_id=course_id)
    if course_features.discussions:
        write_social_engagement_report_on_csv(writer, course_id, company_id)

    return response

def write_engagement_summary_on_csv(csv_writer, course_id, company_id):
    course_engagement_summary = get_course_engagement_summary(course_id, company_id)

    csv_writer.writerow([_('Engagement Summary'), _('# of people'), _('% total cohort'), _('Avg Progress')])
    for stat in course_engagement_summary:
        csv_writer.writerow([stat['name'], stat['people'], stat['invited'], stat['progress']])

def write_participant_performance_on_csv(csv_writer):
    csv_writer.writerow([])
    csv_writer.writerow([_('Participant Performance'), _('% completion'), _('Score')])
    csv_writer.writerow([_('Group work 1'), '-', '-'])
    csv_writer.writerow([_('Group work 2'), '-', '-'])
    csv_writer.writerow([_('Mid-course assessment'), '-', '-'])
    csv_writer.writerow([_('Final assessment'), '-', '-'])


def write_social_engagement_report_on_csv(csv_writer, course_id, company_id):
    course_social_engagement = get_course_social_engagement(course_id, company_id)

    csv_writer.writerow([])
    csv_writer.writerow([_('Social Engagement'), '#'])
    for stat in course_social_engagement:
        csv_writer.writerow([stat['name'], stat['value']])


def get_organization_active_courses(request, company_id):
    permission_handler = Permissions(request.user.id)
    user_organizations = permission_handler.get_all_user_organizations_with_permissions()
    user_main_companies = [user_org.id for user_org in user_organizations["main_company"]]

    is_main_company = int(company_id) in user_main_companies

    company_courses = organization_api.get_organizations_courses(company_id)
    courses = []

    company_admin_group_id = permission_handler.get_group_id(PERMISSION_GROUPS.COMPANY_ADMIN)
    company_admin_ids = [
        user['id'] for user in organization_api.get_users_from_organization_group(company_id, company_admin_group_id)
    ]

    for company_course in company_courses:
        course = {}
        course['name'] = clean_xss_characters(company_course['name'])
        course['id'] = company_course['id']
        course['participants'] = len(company_course['enrolled_users'])
        course_roles = course_api.get_users_filtered_by_role(company_course['id'])
        for user_id in company_course['enrolled_users']:
            not_active_user = any(role.id == user_id for role in course_roles)
            admin_from_different_company = not is_main_company and user_id == request.user.id

            # If another company admin is made company admin of this company, then
            # his courses also get included in `company_courses`, we need to
            # filter them out
            if user_id in company_admin_ids:
                user_organizations = user_api.get_user_organizations(user_id)
                if user_organizations:
                    user_main_company = user_organizations[0]
                    if int(company_id) != user_main_company.id:
                        not_active_user = True

            if not_active_user or admin_from_different_company:
                course['participants'] -= 1

        # Skip courses having no active participant
        if not course['participants']:
            continue

        course['start'] = parsedate(company_course['start'])
        if company_course['end'] is not None:
            course['end'] = parsedate(company_course['end'])
        else:
            course['end'] = None
        course['cohort'] = '-'

        courses.append(course)

    return courses


def edit_course_meta_data(course_id, lesson_label, module_label,
                          lesson_label_flag, module_label_flag):
    data_saved = False
    course_meta_data, created = CourseMetaData.objects.get_or_create(course_id=course_id)

    if lesson_label_flag == 'true':
        if not special_characters_match(lesson_label):
            course_meta_data.lesson_label = lesson_label
            data_saved = True

    if module_label_flag == 'true':
        if not special_characters_match(module_label):
            course_meta_data.module_label = module_label
            data_saved = True

    course_meta_data.save()

    return data_saved


def _get_user_managers(username):
    user_manager_response = manager_api.get_user_manager(username)
    user_managers = None
    if user_manager_response is not None:
        user_managers = user_manager_response["results"]
    return user_managers


def get_user_company_fields(user_id, organization_id):
    org_fields = get_organization_fields(organization_id)
    fields_keys = ','.join([field.get('key') for field in org_fields])
    fields_value = get_company_fields_value_for_user(user_id, organization_id, fields_keys)
    result = {field['key']: field for field in fields_value}

    for field in org_fields:
        field['value'] = result.get(field['key'], {}).get('value')
    return org_fields


def update_user_company_fields_value(user_id, values):
    if not values.get('company'):
        return
    else:
        organization_id = values.get('company')
        fields = get_organization_fields(organization_id)
        fields = [(field['key'], values.get(field['key'])) for field in fields if values.get(field['key'])]
        update_user_company_field_values(user_id, organization_id, fields)
