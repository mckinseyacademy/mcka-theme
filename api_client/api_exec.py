from json_object import JsonParser as JP, JsonObject
import urllib2 as url_access
import models

API_SERVER_ADDRESS = 'http://localhost:8000'
USER_API = 'user_api/v1/users'

def authenticate(username, password):
    response = url_access.urlopen('{}/session'.format(API_SERVER_ADDRESS))
    ar = JP.from_json(response.read(), AuthenticationResponse)
    return ar.session_key

def get_user(user_id):
    response = url_access.urlopen('{}/{}/{}'.format(API_SERVER_ADDRESS, USER_API, user_id))
    return JP.from_json(response.read(), models.UserResponse)

def _open_url_with_session(url):
    headers = {}
    if request["session_key"]:
        headers["session_key"] = request["session_key"]
    return url_access.urlopen(url, headers)

