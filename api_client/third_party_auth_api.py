from urllib import urlencode
from django.conf import settings
from api_client import user_models
from .json_object import JsonParser as JP
from .json_requests import GET

from api_client.api_error import api_error_protect

USER_API = getattr(settings, 'USER_API', 'api/server/users')
THIRD_PARTY_AUTH_API = getattr(settings, 'THIRD_PARTY_AUTH_API', 'api/third_party_auth/v0')


@api_error_protect
def get_providers_by_email(email):
    qs_params = {'email': email}
    response = GET('{server_addr}/{api}/?{qs_params}'.format(
        server_addr=settings.API_SERVER_ADDRESS,
        api=USER_API,
        qs_params=urlencode(qs_params)
    ))
    users = JP.from_json(response.read(), user_models.UserListResponse).results

    if not users:
        return []

    # should never have two users with same email - if that happened probably there're some problem with DB and auth
    assert len(users) <= 1

    user = users[0]

    response = GET("{server_addr}/{api}/users/{username}".format(
        server_addr=settings.API_SERVER_ADDRESS,
        api=THIRD_PARTY_AUTH_API,
        username=user.username
    ))
    associations = JP.from_json(response.read(), user_models.UserSSOProviderAssociationList)
    return associations.active


