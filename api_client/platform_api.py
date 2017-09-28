"""
Module for edx-platform builtin API calls
"""
import json
import requests
import urlparse

from django.conf import settings

from accounts.middleware.thread_local import get_current_request
from api_client.api_error import api_error_protect
from .json_requests import TIMEOUT


ADVANCED_SETTINGS_API = urlparse.urljoin(
    settings.STUDIO_SERVER_ADDRESS, '/settings/advanced/'
)
JSON_REQUEST_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}


def get_cookies():
    """
    Returns current session cookies
    """
    request = get_current_request()
    if request:
        return dict(
            sessionid=request.COOKIES['sessionid'],
            csrftoken=request.COOKIES['csrftoken']
        )

    return dict()


@api_error_protect
def get_course_advanced_settings(course_id):
    """
    Returns advanced settings for the given course
    """
    response = requests.get(
        urlparse.urljoin(ADVANCED_SETTINGS_API, course_id),
        cookies=get_cookies(),
        headers=JSON_REQUEST_HEADERS,
        timeout=TIMEOUT
    )
    response.raise_for_status()

    return json.loads(response.content)


@api_error_protect
def update_course_mobile_available_status(course_id, status):
    """
    Updates mobile available advanced setting for given course
    """
    cookies = get_cookies()
    headers = dict(JSON_REQUEST_HEADERS)
    headers['X-CSRFToken'] = cookies['csrftoken']
    data = {
        'mobile_available': {
            'value': status
        }
    }

    response = requests.put(
        urlparse.urljoin(ADVANCED_SETTINGS_API, course_id),
        data=json.dumps(data),
        cookies=cookies,
        headers=headers,
        timeout=TIMEOUT
    )
    response.raise_for_status()

    return json.loads(response.content)
