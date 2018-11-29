from django.conf import settings

from .json_object import JsonParser as JP
from .api_error import api_error_protect
from .oauth2_requests import get_oauth2_session

USER_MANAGER_API = getattr(settings, 'USER_MANAGER_API', 'api/user_manager/v1/users')


@api_error_protect
def get_user_manager(user_id):
    '''
    get specified user manager
    user_id: it can be either username or email
    '''
    edx_oauth2_session = get_oauth2_session()

    url = '{}/{}/{}/{}'.format(
            settings.API_SERVER_ADDRESS, USER_MANAGER_API, user_id, 'managers'
        )

    response = edx_oauth2_session.get(url)
    return response.json()


@api_error_protect
def post_user_manager(user_id, manager_email):
    '''
    create specified user manager
    user_id: it can be either username or email
    '''
    edx_oauth2_session = get_oauth2_session()

    url = '{}/{}/{}/{}/'.format(
            settings.API_SERVER_ADDRESS, USER_MANAGER_API, user_id, 'managers'
        )

    response = edx_oauth2_session.post(url, data={'email': manager_email})
    return JP.from_json(response.content)


@api_error_protect
def delete_user_manager(username, manager_email):
    '''
    delete specified user manager
    username: it can be either username or email
    '''
    edx_oauth2_session = get_oauth2_session()

    url = '{}/{}/{}/{}?user={}'.format(
            settings.API_SERVER_ADDRESS, USER_MANAGER_API, username, 'managers', manager_email
        )

    response = edx_oauth2_session.delete(url)

    return response.content
