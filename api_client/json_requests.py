''' GET, POST, DELETE, PUT requests for json client '''
import json
from urllib.request import urlopen, build_opener, Request, HTTPHandler
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
    request = get_current_request()
    if request:
        token = request.META.get("HTTP_AUTHORIZATION")
        if token and "Bearer" in token:
            # Token will be passed to authorize mobile request on apros
            headers["Authorization"] = token
    return headers

    if request:
        remote_session_key = request.session.get('remote_session_key')
        if remote_session_key:
            headers['Cookie'] += ";sessionid={};".format(remote_session_key)
    return headers


def GET(url_path):
    ''' GET request wrapper to json web server '''
    url_request = Request(url=url_path, headers=json_headers())
    return urlopen(url=url_request, timeout=TIMEOUT)


def POST(url_path, data):
    ''' POST request wrapper to json web server '''
    url_request = Request(url=url_path, headers=json_headers())
    return urlopen(url_request, json.dumps(data).encode("utf-8"), TIMEOUT)


def DELETE(url_path, data=None):
    ''' DELETE request wrapper to json web server '''
    opener = build_opener(HTTPHandler)
    request = Request(url=url_path, headers=json_headers())
    request.get_method = lambda: 'DELETE'
    json_data = json.dumps(data).encode("utf-8") if data is not None else None
    return opener.open(request, json_data, TIMEOUT)


def PUT(url_path, data):
    ''' PUT request wrapper to json web server '''
    opener = build_opener(HTTPHandler)
    request = Request(
        url=url_path, headers=json_headers(), data=json.dumps(data).encode("utf-8"))
    request.get_method = lambda: 'PUT'
    return opener.open(request, None, TIMEOUT)


def PATCH(url_path, data):
    ''' PATCH request wrapper to json web server '''
    opener = build_opener(HTTPHandler)
    request = Request(
        url=url_path, headers=json_headers(), data=json.dumps(data).encode('utf-8'))
    request.get_method = lambda: 'PATCH'
    return opener.open(request, None, TIMEOUT)
