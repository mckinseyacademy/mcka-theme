'''
Backend for our authentication to delegate auth to api request
Need to implement authenticate, get_user and has_perm
(as specified in documentation)
'''
from django.contrib.auth import get_user_model

from api_client import user_api
from api_client.api_error import ApiError


# pylint: disable=no-member,no-self-use
class JsonBackend(object):

    """
    Authenticate against the remote server using an API call...
    """

    def _load_user(self, user_response, auth_token=None):
        user = get_user_model()()
        user.update_response_fields(user_response, auth_token)
        user.save()
        return user

    def authenticate(self, username=None, password=None, remote_session_key=None):
        '''
        Implements django authenticate that delegates to API
        '''
        if username and password:
            # If remote_session_key is specified, we are attempting to upgrade the remote
            # session from AnonymousUser to an authorized user, using the given credentials.
            # Otherwise a new session will be created.
            auth_info = user_api.authenticate(username, password, remote_session_key=remote_session_key)
            auth_info.user = user_api.get_user(auth_info.user.id)
        elif remote_session_key:
            try:
                auth_info = user_api.get_session(remote_session_key)
                auth_info.user = user_api.get_user(auth_info.user_id)
            except ApiError as err:
                if err.code == 404:
                    return None  # This session ID is not valid
                raise  # This session ID could be valid but an error occurred.
        user = self._load_user(auth_info.user, auth_info.token)
        if hasattr(auth_info, 'csrftoken'):
            user.csrftoken = auth_info.csrftoken

        return user

    def get_user(self, user_id):
        '''
        Fetches user model from cache or via API
        '''
        user = get_user_model().cached_fetch(user_id)
        if user is None:
            try:
                user_response = user_api.get_user(user_id)
                user = self._load_user(user_response)
            except ApiError:
                user = None

        return user

# pylint: disable=unused-argument
    def has_perm(self, user_obj, perm, obj=None):
        '''
        Does the user have permission to do something
        '''
        return True
