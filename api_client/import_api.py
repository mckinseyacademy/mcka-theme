"""
API client methods for the Import API.
"""

import json

from django.conf import settings

from .api_error import api_error_protect
from .json_requests import POST

IMPORT_PARTICIPANTS_API = getattr(settings, 'IMPORT_PARTICIPANTS_API', 'api/server/imports/participants')


@api_error_protect
def import_participant(data, new=True):
    """
    Import a new participant into the LMS, a company and a course.

    Returns the resulting user ID and any errors, respectively.
    """
    url = '{}/{}/{}/'.format(
        settings.API_SERVER_ADDRESS,
        IMPORT_PARTICIPANTS_API,
        'new' if new else 'existing'
    )
    response = json.loads(POST(url, data=data).read())
    return response.get('user_id', 0), response.get('errors', [])
