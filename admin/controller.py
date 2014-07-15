import tempfile
import re

from django.core.servers.basehttp import FileWrapper
from django.utils.translation import ugettext as _
from django.conf import settings

from accounts.middleware.thread_local import set_course_context, get_course_context
from api_client.api_error import ApiError
from api_client import user_api, group_api, course_api, workgroup_api, organization_api
from accounts.models import UserActivation

from .models import Client, WorkGroup

def _load_course(course_id, depth=3, course_api_impl=course_api):
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


def load_course(course_id, depth=3, course_api_impl=course_api):
    '''
    Gets the course from the API, and performs any post-processing for Apros specific purposes
    '''
    course_context = get_course_context()
    if course_context and course_context.get("course_id", None) == course_id and course_context.get("depth", 0) >= depth:
        return course_context["course_content"]

    return _load_course(course_id, depth, course_api_impl)


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


def _register_users_in_list(user_list, client_id, activation_link_head):
    client = Client.fetch(client_id)
    errors = []
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
            errors.append(user_error)
        else:
            print "\nActivation Email for {}:\n".format(user.email), generate_email_text_for_user_activation(activation_record, activation_link_head), "\n\n"

    return errors


def process_uploaded_student_list(file_stream, client_id, activation_link_head):
    # 1) Build user list
    user_list = _build_student_list_from_file(file_stream)
    attempted_count = len(user_list)

    errors = [user_info["error"] for user_info in user_list if "error" in user_info]
    user_list = [user_info for user_info in user_list if "error" not in user_info]

    # 2) Register the users, and associate them with client
    errors.extend(_register_users_in_list(user_list, client_id, activation_link_head))
    failed_count = len(errors)

    # 3) Return any error information
    return {
        "attempted": attempted_count,
        "failed": failed_count,
        "errors": errors
    }


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
    user_strings = [_formatted_user_string(get_user_with_activation(user.id, activation_link)) for user in user_list]

    return '\n'.join(user_strings)

def get_user_with_activation(user_id, activation_link):
    user = user_api.get_user(user_id)
    try:
        activation_record = UserActivation.get_user_activation(user)
        if activation_record:
            user.activation_link = "{}/{}".format(activation_link, activation_record.activation_key)
        else:
            user.activation_link = 'Activated'
    except:
        user.activation_link = 'Could not fetch activation record'

    return user

def get_group_list_as_file(groups):
    group_string = [_formatted_group_string(group) for group in groups]
    return '\n'.join(group_string)


def fetch_clients_with_program(program_id):
    clients = group_api.get_organizations_in_group(program_id, group_object=Client)
    for client in clients:
        try:
            client.places_allocated, client.places_assigned = license_controller.licenses_report(program_id, client.id)
        except:
            client.places_allocated = None
            client.places_assigned = None

    return clients

def filterGroupsAndStudents(course, students):
    ''' THIS IS A VERY SLOW PART OF CODE.
        Due to api limitations, filtering of user from student list has to be done on client.
        It has to have 3 nested "for" loops, and one after (indexes issue in for loop).
        This should be replaced once API changes.
    '''
    groupsList = []
#    for module in course.group_projects:
#        groupsList = groupsList + [WorkGroup.fetch(group.workgroup_id)
#                                   for group in course_api.get_course_content_workgroups(course.id, module.id)]

    groups = []
    groups = workgroup_api.get_workgroups()
#    for workgroup in groupsList:
#        groups.append(workgroup_api.get_groups_by_type(workgroup.id, 'organization'))

    groupedStudents = []
    for group in groups:
        for user in group.users:
            for student in students:
                if user.username == student.username:
                    try:
                        user.company = student.company
                    except:
                        pass
                    groupedStudents.append(student)
        group.students_count = len(group.users)
    #    groups.append(group)

#    groups.sort(key=lambda group: group.id)

    for student in groupedStudents:
        if student in students:
            students.remove(student)

    return groups, students

def getStudentsWithCompanies(course):
    students = course_api.get_user_list(course.id)

    users_ids = [str(user.id) for user in students]
    users = user_api.get_users([{'key': 'ids', 'value': ','.join(users_ids)}])
    students = users.results

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
    try:
        privateFlag = True
        companyid = postValues['students[0][data_field]']
        if companyid == '':
            privateFlag == False
        while(postValues['students[{}][id]'.format(i)]):
            students.append({'id': postValues['students[{}][id]'.format(i)],
                            'company_id': postValues['students[{}][data_field]'.format(i)]})
            if(postValues['students[{}][data_field]'.format(i)] != companyid):
                privateFlag = False
            i = i + 1
    except:
        pass

    return students, companyid, privateFlag
