''' GET, POST, DELETE, PUT requests for json client '''
import urllib2 as url_access
import json
from django.conf import settings
from accounts.middleware.thread_local import get_current_request

# nice to have capitalised names for familiar GET, POST, DELETE, PUT
# pylint: disable=invalid-name

JSON_HEADERS = {
    "Content-Type": "application/json",
    "X-Edx-Api-Key": settings.EDX_API_KEY,
    "Cookie": "edx_splash_screen=mckinsey%2Bacademy"
}


def json_headers():
    # TODO: Add this in when API can deal with requests that have session but not csrf_token
    return JSON_HEADERS
    
    headers = JSON_HEADERS.copy()
    request = get_current_request()
    if request:
        remote_session_key = request.session.get('remote_session_key')
        if remote_session_key:
            headers['Cookie'] += ";sessionid={};".format(remote_session_key)
    return headers


def GET(url_path):
    ''' GET request wrapper to json web server '''
    url_request = url_access.Request(url=url_path, headers=json_headers())
    return url_access.urlopen(url_request)


def POST(url_path, data):
    ''' POST request wrapper to json web server '''
    url_request = url_access.Request(url=url_path, headers=json_headers())
    return url_access.urlopen(url_request, json.dumps(data))


def DELETE(url_path):
    ''' DELETE request wrapper to json web server '''
    opener = url_access.build_opener(url_access.HTTPHandler)
    request = url_access.Request(url=url_path, headers=json_headers())
    request.get_method = lambda: 'DELETE'
    return opener.open(request)


def PUT(url_path, data):
    ''' PUT request wrapper to json web server '''
    opener = url_access.build_opener(url_access.HTTPHandler)
    request = url_access.Request(
        url=url_path, headers=json_headers(), data=json.dumps(data))
    request.get_method = lambda: 'PUT'
    return opener.open(request)
