"""
Module for edx-platform builtin API calls
"""
import json
import urlparse

from django.conf import settings

from .http_request_methods import GET, PUT, SESSION_AUTH


ADVANCED_SETTINGS_API = urlparse.urljoin(
    settings.STUDIO_SERVER_ADDRESS, '/settings/advanced/'
)


def get_course_advanced_settings(course_id):
    """
    Returns advanced settings for the given course
    """
    response = GET(
        urlparse.urljoin(ADVANCED_SETTINGS_API, course_id),
        auth=SESSION_AUTH
    )

    return json.loads(response.content)


def update_course_mobile_available_status(course_id, status):
    """
    Updates mobile available advanced setting for given course
    """
    data = {
        'mobile_available': {
            'value': status
        }
    }

    response = PUT(
        urlparse.urljoin(ADVANCED_SETTINGS_API, course_id),
        data,
        auth=SESSION_AUTH
    )

    return json.loads(response.content)
