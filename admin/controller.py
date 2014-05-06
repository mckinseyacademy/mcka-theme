import tempfile
from urllib2 import HTTPError
from django.core.servers.basehttp import FileWrapper
from django.utils.translation import ugettext as _

from api_client import user_api, group_api
from accounts.models import UserActivation
from .models import Client


def _process_line(user_line):
    try:
        fields = user_line.strip().split(',')
        # format is email,username,password,firstname,lastname (last 3 are optional)

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


def _register_users_in_list(user_list, client_id):
    errors = []
    for user_dict in user_list:
        user = None
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

            errors.append(_("User not registered {} - {} ({})").format(
                    reason, user_dict["email"],
                    user_dict["username"]
                )
            )

        if user:
            try:
                UserActivation.user_activation(user)
                group_api.add_user_to_group(user.id, client_id)
            except HTTPError, e:
                reason = _("Error associating user with client")
                errors.append(_("User not associated with client {} - {} ({})").format(
                        reason,
                        user_dict["email"],
                        user_dict["username"]
                    )
                )

    return errors


def process_uploaded_student_list(file_stream, client_id):
    # 1) Build user list
    user_list = _build_student_list_from_file(file_stream)
    attempted_count = len(user_list)

    errors = [user_info["error"] for user_info in user_list if "error" in user_info]
    user_list = [user_info for user_info in user_list if "error" not in user_info]

    # 2) Register the users, and associate them with
    errors.extend(_register_users_in_list(user_list, client_id))
    failed_count = len(errors)

    # 3) Return any error information
    return {
        "attempted": attempted_count,
        "failed": failed_count,
        "errors": errors
    }


def _formatted_user_string(user):
    return "{},{},,{},{}".format(
        user.email,
        user.username,
        user.first_name,
        user.last_name,
    )


def get_student_list_as_file(client):
    user_list = client.get_users()
    user_strings = [_formatted_user_string(user) for user in user_list]

    return '\n'.join(user_strings)


def fetch_clients_with_program(program_id):
    return [client for client in Client.list() if program_id in [program.id for program in client.fetch_programs()]]
