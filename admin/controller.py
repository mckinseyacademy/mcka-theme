import tempfile
import re

from django.utils.translation import ugettext as _
from django.conf import settings

from accounts.middleware.thread_local import set_course_context, get_course_context
from api_client.api_error import ApiError
from api_client import user_api, group_api, course_api, organization_api, project_api
from accounts.models import UserActivation
from datetime import datetime
from pytz import UTC

from .models import Client, WorkGroup, UserRegistrationError, GROUP_PROJECT_V2_ACTIVITY_CATEGORY

import threading
import Queue
import atexit

GROUP_PROJECT_CATEGORY = 'group-project'
GROUP_PROJECT_V2_CATEGORY = 'group-project-v2'


class GroupProject(object):
    def __init__(self, project_id, name, activities):
        self.id = project_id
        self.name = name
        self.activities = activities

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
    process_uploaded_student_list(
        student_list, client_id, absolute_uri, reg_status)


def _find_group_project_v2_blocks_in_chapter(chapter):
    return (
        (xblock, sequential)
        for sequential in chapter.sequentials
        for page in sequential.pages
        for xblock in page.children
        if xblock.category == GROUP_PROJECT_V2_CATEGORY
    )

def _load_course(course_id, depth=5, course_api_impl=course_api):
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
                chapter.id, chapter.name[len(settings.GROUP_PROJECT_IDENTIFIER):],
                group_project_sequentials
            )
            course.group_projects.append(group_project)
        elif is_group_project_v2_chapter(chapter):
            blocks = _find_group_project_v2_blocks_in_chapter(chapter)
            projects = [GroupProject(block.id, block.name, block.children) for block, seq in blocks]
            course.group_projects.extend(projects)

    # Only the first discussion chapter is taken into account
    course.discussion = None
    discussions = [chapter for chapter in course.chapters if chapter.name.startswith(settings.DISCUSSION_IDENTIFIER)]
    if len(discussions) > 0:
        course.discussion = discussions[0]

    course.chapters = [chapter for chapter in course.chapters if is_normal_chapter(chapter)]

    set_course_context(course, depth)

    return course


def load_course(course_id, depth=5, course_api_impl=course_api, request=None):
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


def _build_student_list_from_file(file_stream):
    # Don't need to read into a tmep file if small enough
    user_objects = []
    with tempfile.TemporaryFile() as temp_file:
        for chunk in file_stream.chunks():
            temp_file.write(chunk)

        temp_file.seek(0)

        # ignore first line
        user_objects = [_process_line(user_line) for user_line in temp_file.read().splitlines()[1:]]

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
            print user_error
            error = UserRegistrationError.create(error=user_error, task_key=reg_status.task_key)
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
