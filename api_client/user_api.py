''' API calls with respect to users and authentication '''
from django.conf import settings
from urllib2 import HTTPError
import json

from .json_object import JsonParser as JP
from . import user_models
from .json_requests import GET, POST, DELETE

AUTH_API = 'api/sessions'
USER_API = 'api/users'
GROUP_API = 'api/groups'

VALID_USER_KEYS = ["email", "first_name", "last_name", "full_name", "city", "country", "username", "level_of_education", "password", "gender", "title", "is_active"]

def _clean_user_keys(user_hash):
    return {user_key: user_hash[user_key] for user_key in VALID_USER_KEYS if user_key in user_hash}


def authenticate(username, password):
    ''' authenticate to the API server '''
    data = {
        "username": username,
        "password": password
    }
    response = POST(
        '{}/{}/'.format(settings.API_SERVER_ADDRESS, AUTH_API),
        data
    )
    return JP.from_json(response.read(), user_models.AuthenticationResponse)


def get_user(user_id):
    ''' get specified user '''
    response = GET(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS, USER_API, user_id
        )
    )
    return JP.from_json(response.read(), user_models.UserResponse)


def delete_session(session_key):
    ''' delete associated openedx session '''
    DELETE(
        '{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            AUTH_API,
            session_key
        )
    )


def register_user(user_hash):
    ''' register the given user within the openedx server '''
    response = POST(
        '{}/{}'.format(settings.API_SERVER_ADDRESS, USER_API),
        _clean_user_keys(user_hash)
    )
    return JP.from_json(response.read())


def _update_user(user_id, user_hash):
    ''' update the given user's information within the openedx server '''
    response = POST(
        '{}/{}/{}'.format(settings.API_SERVER_ADDRESS, USER_API, user_id),
        user_hash
    )
    return JP.from_json(response.read())

def update_user_information(user_id, user_hash):
    ''' update the given user's information within the openedx server '''
    return _update_user(user_id, _clean_user_keys(user_hash))

def activate_user(user_id):
    ''' activate the given user on the openedx server '''
    return _update_user(user_id, {"is_active": True})

def get_user_courses(user_id):
    ''' get the user's summary for their courses '''
    response = GET(
        '{}/{}/{}/courses'.format(
            settings.API_SERVER_ADDRESS,
            USER_API,
            user_id
        )
    )
    courses = JP.from_json(response.read(), user_models.UserCourse)
    # TODO: Faking status for now, need to remove somehow
    for course in courses:
        course.percent_complete = 25

    return courses

def get_user_groups(user_id, group_type=None):
    ''' get the groups in which this user is a member '''
    url = '{}/{}/{}/groups'.format(
        settings.API_SERVER_ADDRESS,
        USER_API,
        user_id,
    )

    if group_type:
        url += "?type={}".format(group_type)

    response = GET(url)

    return JP.from_json(response.read()).groups

def enroll_user_in_course(user_id, course_id):
    ''' enrolls the user summary in the given course '''
    data = {"course_id": course_id}
    response = POST(
        '{}/{}/{}/courses'.format(
            settings.API_SERVER_ADDRESS,
            USER_API,
            user_id
        ),
        data
    )

    courses = JP.from_json(response.read(), user_models.UserCourse)


def get_user_course_detail(user_id, course_id):
    ''' get details for the user for this course'''
    response = GET(
        '{}/{}/{}/courses/{}'.format(
            settings.API_SERVER_ADDRESS,
            USER_API,
            user_id,
            course_id
        )
    )

    return JP.from_json(response.read(), user_models.UserCourseStatus)


def _set_course_position(user_id, course_id, parent_id, child_id):
    data = {
        "position": {
            "parent_content_id": parent_id,
            "child_content_id": child_id,
        }
    }

    response = POST(
        '{}/{}/{}/courses/{}'.format(
            settings.API_SERVER_ADDRESS,
            USER_API,
            user_id,
            course_id
        ),
        data
    )

    # return JP.from_json(response.read())

    return True


def set_user_bookmark(user_id, course_id, chapter_id, sequential_id, page_id):
    '''
    Let the openedx server know the most recently visited page
    Can also provide a None value for chapter_id, then it just sets the page
    within the sequential_id
    '''

    positions = []

    if chapter_id:
        positions.append(_set_course_position(
                user_id,
                course_id,
                course_id,
                chapter_id
            )
        )
        positions.append(_set_course_position(
                user_id,
                course_id,
                chapter_id,
                sequential_id
            )
        )

    positions.append(_set_course_position(
            user_id,
            course_id,
            sequential_id,
            page_id
        )
    )

    return positions


def is_user_in_group(user_id, group_id):
    ''' checks group membership '''
    try:
        response = GET(
            '{}/{}/{}/users/{}'.format(
                settings.API_SERVER_ADDRESS,
                GROUP_API,
                group_id,
                user_id,
            )
        )
    except HTTPError, e:
        if e.code == 404:
            return False
        else:
            raise e

    return (response.code == 200)


def set_user_preferences(user_id, preference_dictionary):
    ''' sets users preferences information '''
    response = POST(
        '{}/{}/{}/preferences'.format(
            settings.API_SERVER_ADDRESS,
            USER_API,
            user_id,
        ),
        preference_dictionary
    )

    return True


def get_user_preferences(user_id):
    ''' sets users preferences information '''
    response = GET(
        '{}/{}/{}/preferences'.format(
            settings.API_SERVER_ADDRESS,
            USER_API,
            user_id,
        ),
    )

    # Note that we return plain dictionary here - makes more sense 'cos we set a dictionary
    return json.loads(response.read())
