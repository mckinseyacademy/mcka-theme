from django.utils.translation import ugettext as _
import urllib2 as url_access
import datetime

from api_client import user_api
from api_client.json_object import JsonParser as JP

CURRENT_COURSE_ID = "current_course_id"

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
    course_id = request.session.get(CURRENT_COURSE_ID, None)

    if not course_id and request.user:
        course_id = user_api.get_user_preferences(request.user.id).get(CURRENT_COURSE_ID, None)

    if not course_id and request.user:
        courses = user_api.get_user_courses(request.user.id)
        if len(courses) > 0:
            course_id = courses[0].id

    return course_id


def set_current_course_for_user(request, course_id):
    prev_course_id = request.session.get(CURRENT_COURSE_ID, None)
    if prev_course_id != course_id:
        request.session[CURRENT_COURSE_ID] = course_id
        user_api.set_user_preferences(
            request.user.id,
            {
                CURRENT_COURSE_ID: course_id,
            }
        )

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

def is_future_start(date):
    current_time = datetime.datetime.now()
    if date <= current_time:
        return False
    else:
        return True
