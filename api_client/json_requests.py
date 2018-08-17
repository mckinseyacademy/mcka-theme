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
}

TIMEOUT = 40


def json_headers():
    # TODO: Add this in when API can deal with requests that have session but
    # not csrf_token
    headers = JSON_HEADERS.copy()
    return headers

    if request:
        remote_session_key = request.session.get('remote_session_key')
        if remote_session_key:
            headers['Cookie'] += ";sessionid={};".format(remote_session_key)
    return headers


def GET(url_path):
    ''' GET request wrapper to json web server '''
    url_request = url_access.Request(url=url_path, headers=json_headers())
    return url_access.urlopen(url=url_request, timeout=TIMEOUT)


def POST(url_path, data):
    ''' POST request wrapper to json web server '''
    url_request = url_access.Request(url=url_path, headers=json_headers())
    return url_access.urlopen(url_request, json.dumps(data), TIMEOUT)


def DELETE(url_path, data=None):
    ''' DELETE request wrapper to json web server '''
    opener = url_access.build_opener(url_access.HTTPHandler)
    request = url_access.Request(url=url_path, headers=json_headers())
    request.get_method = lambda: 'DELETE'
    json_data = json.dumps(data) if not data is None else None
    return opener.open(request, json_data, TIMEOUT)


def PUT(url_path, data):
    ''' PUT request wrapper to json web server '''
    opener = url_access.build_opener(url_access.HTTPHandler)
    request = url_access.Request(
        url=url_path, headers=json_headers(), data=json.dumps(data))
    request.get_method = lambda: 'PUT'
    return opener.open(request, None, TIMEOUT)


def PATCH(url_path, data):
    ''' PATCH request wrapper to json web server '''
    opener = url_access.build_opener(url_access.HTTPHandler)
    request = url_access.Request(
        url=url_path, headers=json_headers(), data=json.dumps(data))
    request.get_method = lambda: 'PATCH'
    return opener.open(request, None, TIMEOUT)
