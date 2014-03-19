from json_object import JsonParser as JP, JsonObject
import models
from json_requests import GET, POST, DELETE, PUT

from django.conf import settings

AUTH_API = 'api/system/v1/sessions'
USER_API = 'api/system/v1/users'


def authenticate(username, password):
    data = {
        "username": username,
        "password": password
    }
    response = POST('{}/{}'.format(settings.API_SERVER_ADDRESS, AUTH_API), data)
    return JP.from_json(response.read(), models.AuthenticationResponse)


def get_user(user_id):
    response = GET('{}/{}/{}'.format(settings.API_SERVER_ADDRESS, USER_API, user_id))
    return JP.from_json(response.read(), models.UserResponse)


def delete_session(session_key):
    DELETE('{}/{}/{}'.format(settings.API_SERVER_ADDRESS, AUTH_API, session_key))


def register_user(user_hash):
    user_keys = ["username", "first_name", "last_name", "email", "password"]
    data = {user_key: user_hash[user_key] for user_key in user_keys}

    response = POST('{}/{}'.format(settings.API_SERVER_ADDRESS, USER_API), data)
    return JP.from_json(response.read())
