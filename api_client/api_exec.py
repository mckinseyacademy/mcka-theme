from json_object import JsonParser as JP, JsonObject
import urllib2 as url_access
import models
import json

API_SERVER_ADDRESS = 'http://localhost:8000'
AUTH_API = 'api/system/v1/sessions'
USER_API = 'user_api/v1/users'


def authenticate(username, password):
    data = {
        "username": username,
        "password": password
    }
    url_request = url_access.Request(url='{}/{}'.format(API_SERVER_ADDRESS, AUTH_API), headers={"Content-Type": "application/json"})
    response = url_access.urlopen(url_request, json.dumps(data))
    return JP.from_json(response.read(), models.AuthenticationResponse)


def get_user(user_id):
    response = url_access.urlopen('{}/{}/{}'.format(API_SERVER_ADDRESS, USER_API, user_id))
    return JP.from_json(response.read(), models.UserResponse)


def _open_url_with_session(url):
    headers = {}
    if request["session_key"]:
        headers["session_key"] = request["session_key"]
    return url_access.urlopen(url, headers)


def delete_session(session_key):
    opener = url_access.build_opener(url_access.HTTPHandler)
    request = url_access.Request(url='{}/{}/{}'.format(API_SERVER_ADDRESS, AUTH_API, session_key), headers={"Content-Type": "application/json"})
    request.get_method = lambda: 'DELETE'
    url = opener.open(request)
