import tempfile
from urllib2 import HTTPError
from django.core.servers.basehttp import FileWrapper

from api_client import user_api, group_api


def _process_line(user_line):
    fields = user_line.split(',')
    # format is email,username,password,firstname,lastname

    # Must have the first 3 fields
    user_info = {
        "email": fields[0],
        "username": fields[1],
        "password": fields[2],
    }
    if len(fields) > 4:
        user_info["first_name"] = fields[3]
        user_info["last_name"] = fields[4]

    return user_info


def _build_student_list_from_file(file_stream):
    # Don't need to read into a tmep file if small enough
    user_objects = []
    with tempfile.TemporaryFile() as temp_file:
        for chunk in file_stream.chunks():
            temp_file.write(chunk)

        temp_file.seek(0)
        user_objects = [_process_line(user_line) for user_line in temp_file]

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
            reason = "Error processing user registration"
            if e.code == 409:
                reason = "Username or email already registered"

            errors.append("User not registered {} - {} ({})".format(
                    reason, user_dict["email"],
                    user_dict["username"]
                )
            )

        if user:
            try:
                group_api.add_user_to_group(user.id, client_id)
            except HTTPError, e:
                reason = "Error associating user with client"
                errors.append("User not associated with client {} - {} ({})".format(
                        reason,
                        user_dict["email"],
                        user_dict["username"]
                    )
                )

    return errors


def process_uploaded_student_list(file_stream, client_id):
    # 1) Build user list
    user_list = _build_student_list_from_file(file_stream)

    # 2) Register the users, and associate them with
    errors = _register_users_in_list(user_list, client_id)

    # 3) Return any error information
    return errors


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
