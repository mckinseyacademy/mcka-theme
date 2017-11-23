# Api calls related to mobileapps

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