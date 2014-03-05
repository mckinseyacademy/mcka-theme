from json_object import JsonParser as JP, JsonObject
import urllib2 as url_access
import models

API_SERVER_ADDRESS = 'http://localhost:8005'

def authenticate(username, password):
    response = url_access.urlopen('{}/session'.format(API_SERVER_ADDRESS))
    ar = JP.from_json(response.read(), AuthenticationResponse)
    return ar.session_key

def get_user(user_id):
    response = url_access.urlopen('{}/users/{}'.format(API_SERVER_ADDRESS, user_id))
    return JP.from_json(response.read(), UserResponse)

