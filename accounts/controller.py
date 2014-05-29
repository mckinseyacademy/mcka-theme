from django.utils.translation import ugettext as _
import urllib2 as url_access

from api_client import user_api
from api_client.json_object import JsonParser as JP

class ActivationError(Exception):

    '''
    Exception to be thrown when an activation failure occurs
    '''

    def __init__(self, value):
        self.value = value
        super(ActivationError, self).__init__()

    def __str__(self):
        return "ActivationError '{}'".format(self.value)


def get_current_course_for_user(request):
    course_id = request.session.get("current_course_id", None)

    if not course_id and request.user:
        # TODO: Replace with logic for finding "current" course
        # For now, we just return first course
        courses = user_api.get_user_courses(request.user.id)
        if len(courses) > 0:
            course_id = courses[0].id

    return course_id

def get_current_course_by_user_id(user_id):
    # TODO: Replace with logic for finding "current" course
    # For now, we just return first course
    courses = user_api.get_user_courses(user_id)
    if len(courses) > 0:
        course_id = courses[0].id
        return course_id
    return None


def user_activation_with_data(user_id, user_data, activation_record):
    try:
        # Make sure they'll be inactive while updating fields, then we explicitly activate them
        user_data["is_active"] = False
        updated_user = user_api.update_user_information(user_id, user_data)
    except url_access.HTTPError, err:
        error = _("An error occurred updating user information")
        error_messages = {
            409: _(("User with matching username "
                    "or email already exists"))
        }
        if err.code in error_messages:
            error = error_messages[err.code]

        response_information = JP.from_json(err.read())
        if hasattr(response_information, "message"):
            error = response_information.message

        raise ActivationError(error)

    # if we are still okay, then activate in a separate operation
    try:
        user_api.activate_user(user_id)
    except url_access.HTTPError, err:
        error = _("An error occurred activating user")
        response_information = JP.from_json(err.read())
        if hasattr(response_information, "message"):
            error = response_information.message

        raise ActivationError(error)

    activation_record.delete()
