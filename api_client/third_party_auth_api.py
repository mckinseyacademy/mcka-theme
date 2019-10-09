from urllib.error import HTTPError

from django.conf import settings

from api_client import user_models
from api_client.api_error import api_error_protect
from .json_object import JsonParser as JP
from .json_requests import GET

USER_API = getattr(settings, 'USER_API', 'api/server/users')
THIRD_PARTY_AUTH_API = getattr(settings, 'THIRD_PARTY_AUTH_API', 'api/third_party_auth/v0')


@api_error_protect
def get_providers_by_login_id(login_id):
    try:
        response = GET('{server_addr}/{api}/users/{login_id}'.format(
            server_addr=settings.API_SERVER_ADDRESS,
            api=THIRD_PARTY_AUTH_API,
            login_id=login_id,
        ))
    except HTTPError as e:
        if e.code == 404:
            return []
        else:
            raise
    associations = JP.from_json(response.read(), user_models.UserSSOProviderAssociationList)
    return associations.active
