"""
Api calls related to mobileapps
"""
from django.conf import settings
from urllib import urlencode

from .api_error import api_error_protect
from .oauth2_requests import get_oauth2_session


MOBILE_APP_API = getattr(settings, 'MOBILE_APP_API', 'api/server/mobileapps')


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
    response = get_oauth2_session().put(url, data=params)
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
    response = get_oauth2_session().post(url, params)
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
    response = get_oauth2_session().delete(url, data=params)
    return response
