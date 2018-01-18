"""
Api calls related to mobileapps
"""
import json

from django.conf import settings
from urllib import urlencode

from .api_error import api_error_protect
from .oauth2_requests import get_oauth2_session


MOBILE_APP_API = getattr(settings, 'MOBILE_APP_API', 'api/server/mobileapps')
JSON_HEADERS = {"Content-Type": "application/json"}


@api_error_protect
def get_mobile_apps(params):
    """
    Returns filtered list of mobile apps based on query params, Mobile apps can
    be filtered by `app_name`, `organization_ids` and `organization_name`.
    """
    url = '{}/{}?{}'.format(
        settings.API_SERVER_ADDRESS,
        MOBILE_APP_API,
        urlencode(params)
    )
    response = get_oauth2_session().get(url)
    return response.json()


@api_error_protect
def get_mobile_app_details(app_id):
    """
    Returns mobile app details based on app id
    """
    url = '{}/{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        MOBILE_APP_API,
        app_id
    )
    response = get_oauth2_session().get(url)
    return response.json()


@api_error_protect
def update_mobile_app(app_id, params):
    """
    Based on app id update mobile app with updated params
    """
    url = '{}/{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        MOBILE_APP_API,
        app_id
    )
    response = get_oauth2_session().put(url, data=json.dumps(params), headers=JSON_HEADERS)
    return response.json()


@api_error_protect
def append_organization(app_id, params):
    """
    append mobile app organization list with the given organizations
    """
    url = '{}/{}/{}/organizations'.format(
        settings.API_SERVER_ADDRESS,
        MOBILE_APP_API,
        app_id
    )
    response = get_oauth2_session().post(url, data=json.dumps(params), headers=JSON_HEADERS)
    return response


@api_error_protect
def remove_organization(app_id, params):
    """
    remove organization entry from mobile app organization list
    """
    url = '{}/{}/{}/organizations'.format(
        settings.API_SERVER_ADDRESS,
        MOBILE_APP_API,
        app_id
    )

    response = get_oauth2_session().delete(url, data=json.dumps(params), headers=JSON_HEADERS)
    return response


@api_error_protect
def create_mobile_app_theme(organization_id, data, mobile_logo_image=None):
    """
    Create new theme for mobile app for specific organization
    """
    url = '{}/{}/organization/{}/themes'.format(
        settings.API_SERVER_ADDRESS,
        MOBILE_APP_API,
        organization_id
    )
    response = get_oauth2_session().post(url, data=data, files=mobile_logo_image)
    return response


@api_error_protect
def get_mobile_app_themes(organization_id):
    """
    Returns list of active mobile app themes for specific organization
    """
    url = '{}/{}/organization/{}/themes'.format(
        settings.API_SERVER_ADDRESS,
        MOBILE_APP_API,
        organization_id
    )
    response = get_oauth2_session().get(url)
    return response.json()['results']


@api_error_protect
def update_mobile_app_theme(mobile_app_theme_id, data, mobile_image_upload=None):
    """
    Updates mobile app theme
    """
    url = '{}/{}/themes/{}'.format(
        settings.API_SERVER_ADDRESS,
        MOBILE_APP_API,
        mobile_app_theme_id
    )
    response = get_oauth2_session().patch(url, data=data, files=mobile_image_upload)
    return response
