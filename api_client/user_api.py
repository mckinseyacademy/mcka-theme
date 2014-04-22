''' API calls with respect to users and authentication '''
from .json_object import JsonParser as JP
from . import user_models
from .json_requests import GET, POST, DELETE

from django.conf import settings

AUTH_API = 'api/sessions'
USER_API = 'api/users'
GROUP_API = 'api/groups'


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
    user_keys = ["username", "first_name", "last_name", "email", "password"]
    data = {user_key: user_hash[user_key] for user_key in user_keys}

    response = POST(
        '{}/{}'.format(settings.API_SERVER_ADDRESS, USER_API),
        data
    )
    return JP.from_json(response.read())


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
            "parent_module_id": parent_id,
            "child_module_id": child_id,
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


def set_user_bookmark(user_id, program_id, course_id, chapter_id, sequential_id, page_id):
    ''' let the openedx server know the most recently visited page '''

    positions = []

    positions.append(_set_course_position(user_id, course_id, course_id, chapter_id))
    positions.append(_set_course_position(user_id, course_id, chapter_id, sequential_id))
    positions.append(_set_course_position(user_id, course_id, sequential_id, page_id))

    return positions



def create_group(group_name):
    ''' creates a group '''
    data = {
        "name": group_name
    }

    url = '{}/{}/'.format(settings.API_SERVER_ADDRESS, GROUP_API)
    response = POST(url, data)

    return JP.from_json(response.read())


def is_user_in_group(user_id, group_id):
    ''' checks group membership '''
    response = GET(
        '{}/{}/{}/users/{}'.format(
            settings.API_SERVER_ADDRESS,
            GROUP_API,
            group_id,
            user_id
        )
    )
    if response.code == 200:
        return True
    return False
