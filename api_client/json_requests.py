''' GET, POST, DELETE, PUT requests for json client '''
import urllib2 as url_access
import json

# nice to have capitalised names for familiar GET, POST, DELETE, PUT
# pylint: disable=invalid-name

JSON_HEADERS = {"Content-Type": "application/json"}


def GET(url_path):
    ''' GET request wrapper to json web server '''
    url_request = url_access.Request(url=url_path, headers=JSON_HEADERS)
    return url_access.urlopen(url_request)


def POST(url_path, data):
    ''' POST request wrapper to json web server '''
    url_request = url_access.Request(url=url_path, headers=JSON_HEADERS)
    return url_access.urlopen(url_request, json.dumps(data))


def DELETE(url_path):
    ''' DELETE request wrapper to json web server '''
    opener = url_access.build_opener(url_access.HTTPHandler)
    request = url_access.Request(url=url_path, headers=JSON_HEADERS)
    request.get_method = lambda: 'DELETE'
    return opener.open(request)


def PUT(url_path, data):
    ''' PUT request wrapper to json web server '''
    opener = url_access.build_opener(url_access.HTTPHandler)
    request = url_access.Request(
        url=url_path, headers=JSON_HEADERS, data=json.dumps(data))
    request.get_method = lambda: 'PUT'
    return opener.open(request)
