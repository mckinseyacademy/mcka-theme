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


def set_user_bookmark(user_id, program_id, course_id, chapter_id, page_id):
    ''' let the openedx server know the most recently visited page '''
    data = {
        "program_id": program_id,
        "course_id": course_id,
        "bookmark": {
            "chapter_id": chapter_id,
            "page_id": page_id,
        }
    }
    response = POST(
        '{}/{}/{}/course_bookmark'.format(
            # TODO: remove forced MOCK reference when real API becomes available
            settings.API_MOCK_SERVER_ADDRESS,
            USER_API,
            user_id
        ),
        data
    )
    return JP.from_json(response.read())


def get_groups():
    ''' gets all groups '''
    response = GET(
        '{}/{}'.format(
            settings.API_MOCK_SERVER_ADDRESS, GROUP_API
        )
    )
    groups_json = JP.from_json(response.read())
    rd = {}
    for group in groups_json:
        rd[group.name] = group.id
    return rd


def is_user_in_group(user_id, group_id):
    ''' checks group membership '''
    response = GET(
        '{}/{}/{}/users/{}'.format(
            settings.API_MOCK_SERVER_ADDRESS,
            GROUP_API,
            group_id,
            user_id
        )
    )
    if response.code == 200:
        return True
    return False
