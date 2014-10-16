import tempfile
import re

from django.core.servers.basehttp import FileWrapper
from django.utils.translation import ugettext as _
from django.conf import settings

from accounts.middleware.thread_local import set_course_context, get_course_context
from api_client.api_error import ApiError
from api_client import user_api, group_api, course_api, workgroup_api, organization_api, project_api
from accounts.models import UserActivation
from datetime import datetime
from pytz import UTC

from .models import Client, WorkGroup, UserRegistrationError

import threading
import Queue
import atexit


GROUP_PROJECT_CATEGORY = 'group-project'


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

def _load_course(course_id, depth=4, course_api_impl=course_api):
    '''
    Gets the course from the API, and performs any post-processing for Apros specific purposes
    '''
    def is_normal_chapter(chapter):
        '''
        Check if a chapter is normal or special. GROUP_PROJECT_WORK and DISCUSSION are special chapters.
        '''
        return (not chapter.name.startswith(settings.DISCUSSION_IDENTIFIER) and \
                not chapter.name.startswith(settings.GROUP_PROJECT_IDENTIFIER))

    course = course_api_impl.get_course(course_id, depth)

    # Separate special chapters

    course.group_project_chapters = [chapter for chapter in course.chapters if chapter.name.startswith(settings.GROUP_PROJECT_IDENTIFIER)]

    # Only the first discussion chapter is taken into account
    course.discussion = None
    discussions = [chapter for chapter in course.chapters if chapter.name.startswith(settings.DISCUSSION_IDENTIFIER)]
    if len(discussions) > 0:
        course.discussion = discussions[0]

    course.chapters = [chapter for chapter in course.chapters if is_normal_chapter(chapter)]

    for group_project in course.group_project_chapters:
        group_project.name = group_project.name[len(settings.GROUP_PROJECT_IDENTIFIER):]

    set_course_context(course, depth)

    return course


def load_course(course_id, depth=4, course_api_impl=course_api, request=None):
    '''
    Gets the course from the API, and performs any post-processing for Apros specific purposes
    '''
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
            print "\nActivation Email for {}:\n".format(user.email), generate_email_text_for_user_activation(activation_record, activation_link_head), "\n\n"
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
    return "{},{},{},{},{},{},{},{}".format(
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
    return "{},{},{},{}".format(
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
        group_list_lines.append("{}: {}\n".format(
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

def filter_groups_and_students(group_projects, students):

    group_project_groups = {}
    groupedStudents = []

    for group_project in group_projects:
        groups = project_api.get_project_workgroups(group_project.id, WorkGroup)

        for group in groups:
            group_users = {u.id : u for u in group.users}
            students_in_group = [s for s in students if s.id in group_users.keys()]
            groupedStudents.extend(students_in_group)

            for group_student in students_in_group:
                group_users[group_student.id].company = getattr(group_student, "company", None)

            group.students_count = len(group.users)

        group_project_groups[group_project.id] = groups

    for student in groupedStudents:
        if student in students:
            students.remove(student)

    return group_project_groups, students

def getStudentsWithCompanies(course):
    students = course_api.get_user_list(course.id)

    users_ids = [str(user.id) for user in students]
    additional_fields = ["organizations"]
    students = user_api.get_users(ids=users_ids, fields=additional_fields)

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

def is_group_activity(sequential):
    return len(sequential.pages) > 0 and GROUP_PROJECT_CATEGORY in sequential.pages[0].child_category_list()

def get_group_project_activities(group_project_chapter):
    return [s for s in group_project_chapter.sequentials if is_group_activity(s)]

def get_group_activity_xblock(activity):
    return [gp for gp in activity.pages[0].children if gp.category == GROUP_PROJECT_CATEGORY][0]


def generate_course_report(client_id, course_id, url_prefix, students):

    output_lines = []

    def output_line(line_data_array):
        output_lines.append(','.join(line_data_array))

    activity_names_row = ["Client ID","","Course ID",""]
    output_line(activity_names_row)

    group_header_row = [client_id,"", course_id]
    output_line(group_header_row)

    output_line("--------")

    activity_names_row = ["Full Name","Username","Title","Complete %","Email"]
    output_line(activity_names_row)

    for student in students:
        user_row = [student.full_name,student.username,student.title,"{}%".format(str(student.progress)),student.email]
        output_line(user_row)

    return '\n'.join(output_lines)


def generate_program_report(client_name, program_id, url_prefix, courses, total_avg_grade, total_pet_completed):

    output_lines = []

    def output_line(line_data_array):
        output_lines.append(','.join(line_data_array))

    activity_names_row = ["Client Name","","Program ID",""]
    output_line(activity_names_row)

    group_header_row = [client_name,"", str(program_id)]
    output_line(group_header_row)

    output_line("--------")

    activity_names_row = ["Courses","Participants","Started","Completed","Completed (%)", "Avg. Grade"]
    output_line(activity_names_row)

    for course in courses:
        course_row = [course.name,str(course.metrics.users_enrolled),str(course.metrics.users_started),str(course.metrics.users_grade_complete_count),str(course.metrics.percent_completed)+"%",str(course.metrics.users_grade_average)]
        output_line(course_row)

    total_row = ["","","","Total:",str(total_avg_grade),str(total_pet_completed)]

    output_line(total_row)

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
        metrics.percent_completed = int(int(metrics.users_grade_complete_count) / int(metrics.users_enrolled) * 100)
    return metrics
