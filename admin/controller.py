import tempfile
from urllib2 import HTTPError
from django.core.servers.basehttp import FileWrapper
from django.utils.translation import ugettext as _
from django.conf import settings

from api_client import user_api, group_api, course_api
from accounts.models import UserActivation
from .models import Client

def load_course(course_id, depth=3, course_api_impl=course_api):
    '''
    Gets the course from the API, and performs any post-processing for Apros specific purposes
    '''
    course = course_api_impl.get_course(course_id, depth)

    # Separate Group Projects
    course.group_projects = [chapter for chapter in course.chapters if chapter.name.startswith(settings.GROUP_PROJECT_IDENTIFIER)]
    course.chapters = [chapter for chapter in course.chapters if not chapter.name.startswith(settings.GROUP_PROJECT_IDENTIFIER)]

    for group_project in course.group_projects:
        group_project.name = group_project.name[len(settings.GROUP_PROJECT_IDENTIFIER):]

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
        # format is email,username,password,firstname,lastname,city,country (last 5 are optional)

        # Must have the first 2 fields
        user_info = {
            "email": fields[0],
            "username": fields[1],
            "is_active": False,
        }
        if len(fields) > 2 and len(fields[2].strip()) > 1:
            user_info["password"] = fields[2]
        else:
            user_info["password"] = "initial_P455w0RD!#"

        if len(fields) > 4:
            user_info["first_name"] = fields[3]
            user_info["last_name"] = fields[4]

        if len(fields) > 5:
            user_info["city"] = fields[5]

        if len(fields) > 6:
            user_info["country"] = fields[6]

    except Exception, e:
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

        user_objects = [_process_line(user_line) for user_line in temp_file.read().splitlines()]

    return user_objects


def _register_users_in_list(user_list, client_id, activation_link_head):
    errors = []
    for user_dict in user_list:
        user = None
        user_error = None
        activation_record = None
        try:
            user = user_api.register_user(user_dict)
        except HTTPError, e:
            user = None
            # Error code 409 means that they already exist somehow;
            # build list of errors
            reason = _("Error processing user registration")
            error_messages = {
                409: _("Username or email already registered")
            }
            if e.code in error_messages:
                reason = error_messages[e.code]

            user_error = _("User not registered {} - {} ({})").format(
                reason, user_dict["email"],
                user_dict["username"]
            )

        if user:
            try:
                activation_record = UserActivation.user_activation(user)
                group_api.add_user_to_group(user.id, client_id)
            except HTTPError, e:
                reason = _("Error associating user with client")

                user_error = _("User not associated with client {} - {} ({})").format(
                    reason,
                    user_dict["email"],
                    user_dict["username"]
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
    return "{},{},,{},{},{},{}".format(
        user.email,
        user.username,
        user.first_name,
        user.last_name,
        user.city,
        user.country,
    )

def _formatted_user_string_group_list(user):
    return "{},{},,{},{}".format(
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

def get_student_list_as_file(client):
    user_list = client.get_users()
    user_strings = [_formatted_user_string(user) for user in user_list]

    return '\n'.join(user_strings)

def get_group_list_as_file(groups):  
    group_string = [_formatted_group_string(group) for group in groups]
    return '\n'.join(group_string)


def fetch_clients_with_program(program_id):
    return [client for client in Client.list() if program_id in [program.id for program in client.fetch_programs()]]
