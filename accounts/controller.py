import urllib2 as url_access
import datetime

from django.conf import settings
from django.utils.translation import ugettext as _

from api_client import user_api
from api_client.json_object import JsonParser as JP
from api_client.api_error import ApiError

from admin.models import Program
from license import controller as license_controller


CURRENT_COURSE_ID = "current_course_id"
CURRENT_PROGRAM_ID = "current_program_id"
CURRENT_PROGRAM = "current_program"


class ActivationError(Exception):
    '''
    Exception to be thrown when an activation failure occurs
    '''
    def __init__(self, value):
        self.value = value
        super(ActivationError, self).__init__()

    def __str__(self):
        return "ActivationError '{}'".format(self.value)


def _get_user_programs(user_id):
    ''' Helper function to retrieve the user's programs '''
    return user_api.get_user_groups(user_id, 'series')


def get_current_course_by_user_id(user_id):
    # TODO: Replace with logic for finding "current" course
    # For now, we just return first course
    courses = user_api.get_user_courses(user_id)
    if len(courses) > 0:
        course_id = courses[0].id
        return course_id
    return None


def get_current_course_for_user(request):
    course_id = request.session.get(CURRENT_COURSE_ID, None)

    if not course_id and request.user:
        course_id = user_api.get_user_preferences(request.user.id).get(CURRENT_COURSE_ID, None)

    if not course_id and request.user:
        course_id = get_current_course_by_user_id(request.user.id)

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

        # Additionally set the current program for this user
        current_program = None
        courses = user_api_impl.get_user_courses(request.user.id)
        for program in Program.programs_with_course(course_id):
            if license_controller.fetch_granted_license(program.id, request.user.id) is not None:
                current_program = program
                break
        if current_program:
            program_course_ids = [course.course_id for course in current_program.fetch_courses()]
            if courses:
                current_program.courses = [course for course in courses if course.id in program_course_ids]
                current_program.outside_courses = [course for course in courses if course.id not in program_course_ids]
        else:
            current_program = Program(dictionary={"id": "NO_PROGRAM", "name": settings.NO_PROGRAM_NAME})
            current_program.courses = courses
            current_program.outside_courses = None
        set_current_program_for_user(request, current_program)


def get_current_program_for_user(request):

    # Attempt to load from current session
    program = request.session.get(CURRENT_PROGRAM, None)

    # Attempt to load from user preferences
    if not program and request.user:
        program_id = user_api.get_user_preferences(request.user.id).get(CURRENT_PROGRAM_ID, None)
        if program_id:
            program = Program.fetch(program_id)
            set_current_program_for_user(request, program)

    # Attempt to load first program
    if not program and request.user:
        programs = _get_user_programs(request.user.id)
        if len(programs) > 0:
            program = programs[0]
            set_current_program_for_user(request, program)

    # Return the program to the caller
    return program


def set_current_program_for_user(request, program):
    prev_program = request.session.get(CURRENT_PROGRAM, None)
    if prev_program is None or (prev_program.id != program.id):
        request.session[CURRENT_PROGRAM] = program
        request.session[CURRENT_PROGRAM_ID] = program.id
        user_api.set_user_preferences(
            request.user.id,
            {
                CURRENT_PROGRAM_ID: program.id,
            }
        )


def user_activation_with_data(user_id, user_data, activation_record):
    try:
        # Make sure they'll be inactive while updating fields, then we explicitly activate them
        user_data["is_active"] = False
        updated_user = user_api.update_user_information(user_id, user_data)
    except ApiError as e:
        raise ActivationError(e.message)

    # if we are still okay, then activate in a separate operation
    try:
        user_api.activate_user(user_id)
    except ApiError as e:
        raise ActivationError(e.message)

    activation_record.delete()


def is_future_start(date):
    current_time = datetime.datetime.now()
    if date <= current_time:
        return False
    else:
        return True
