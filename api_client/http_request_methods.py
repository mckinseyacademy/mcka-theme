import json
import requests

from django.conf import settings

from accounts.middleware.thread_local import get_current_request
from api_client.api_error import api_error_protect
from .json_requests import TIMEOUT


API_KEY_AUTH = 1
SESSION_AUTH = 2


def _get_cookies():
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


def _get_auth_based_request_kwargs(auth, **kwargs):
    """
    Returns dictionary of kwargs for request based on authentication type
    Args:
        auth: Authentication type for which request kwargs being generated

    Returns:
        dict: dictionary of kwargs
    """
    kwargs['headers'] = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    kwargs['timeout'] = TIMEOUT

    if auth == API_KEY_AUTH:
        kwargs['headers'].update({'X-Edx-Api-Key': settings.EDX_API_KEY})

    if auth == SESSION_AUTH:
        cookies = _get_cookies()
        kwargs['cookies'] = cookies
        kwargs['headers'].update({'X-CSRFToken': cookies['csrftoken']})

    return kwargs


@api_error_protect
def GET(url, auth=API_KEY_AUTH, **kwargs):
    """
    Helper method to send GET request to given url with given auth type

    Args:
        url: Url to send GET request to.
        auth: Authentication type for this call, default: API_KEY_AUTH
    """
    response = requests.get(
        url,
        **_get_auth_based_request_kwargs(auth, **kwargs)
    )
    response.raise_for_status()

    return response


@api_error_protect
def POST(url, data, auth=API_KEY_AUTH, **kwargs):
    """
    Helper method to send POST request to given url with given authentication
    type and data

    Args:
        url: Url to send POST request to.
        data: JSON object to send as request payload.
        auth: Authentication type for this call, default: API_KEY_AUTH
    """
    response = requests.post(
        url,
        data=json.dumps(data),
        **_get_auth_based_request_kwargs(auth, **kwargs)
    )
    response.raise_for_status()

    return response


@api_error_protect
def PUT(url, data, auth=API_KEY_AUTH, **kwargs):
    """
    Helper method to send PUT request to given url with given authentication
    type and data

    Args:
        url: Url to send PUT request to.
        data: JSON object to send as request payload.
        auth: Authentication type for this call, default: API_KEY_AUTH
    """
    response = requests.put(
        url,
        data=json.dumps(data),
        **_get_auth_based_request_kwargs(auth, **kwargs)
    )
    response.raise_for_status()

    return response


@api_error_protect
def DELET(url, auth=API_KEY_AUTH, **kwargs):
    """
    Helper method to send DELETE request to given url with given auth type

    Args:
        url: Url to send DELETE request to.
        auth: Authentication type for this call, default: API_KEY_AUTH
    """
    response = requests.delete(
        url,
        **_get_auth_based_request_kwargs(auth, **kwargs)
    )
    response.raise_for_status()

    return response
