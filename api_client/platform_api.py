"""
Module for edx-platform builtin API calls
"""
import json
import urllib.parse

from django.conf import settings

from .http_request_methods import GET, PUT, POST, SESSION_AUTH

from api_data_manager.user_data import USER_PROPERTIES
from api_data_manager.signals import user_data_updated


ADVANCED_SETTINGS_API = urllib.parse.urljoin(
    settings.STUDIO_SERVER_ADDRESS, '/settings/advanced/'
)
PLATFORM_USER_API = urllib.parse.urljoin(settings.API_SERVER_ADDRESS, 'api/user/v1/')


def update_user_profile_image(user, file):
    url = urllib.parse.urljoin(
        PLATFORM_USER_API,
        'accounts/{}/image'.format(user.username)
    )

    user_data_updated.send(
        sender=__name__, user_ids=[user.id],
        data_type=USER_PROPERTIES.PROFILE
    )

    return POST(url, {}, auth=SESSION_AUTH, files=file)


def get_course_advanced_settings(course_id):
    """
    Returns advanced settings for the given course
    """
    response = GET(
        urllib.parse.urljoin(ADVANCED_SETTINGS_API, course_id),
        auth=SESSION_AUTH,
        content_type='application/json'
    )

    return json.loads(response.text)


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
        urllib.parse.urljoin(ADVANCED_SETTINGS_API, course_id),
        json.dumps(data),
        auth=SESSION_AUTH,
        content_type='application/json'
    )

    return json.loads(response.text)
