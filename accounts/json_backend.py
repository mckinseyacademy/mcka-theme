'''
Backend for our authentication to delegate auth to api request
Need to implement authenticate, get_user and has_perm
(as specified in documentation)
'''
from django.contrib.auth import get_user_model

from api_client import user_api


# pylint: disable=no-member,no-self-use
class JsonBackend(object):

    """
    Authenticate against the remote server using an API call...
    """

    def authenticate(self, username=None, password=None):
        '''
        Implements django authenticate that delegates to API
        '''
        auth_info = user_api.authenticate(username, password)
        user = get_user_model()()
        user.update_response_fields(auth_info.user, auth_info.token)
        user.save()
        return user

    def get_user(self, user_id):
        '''
        Fetches user model from cache or via API
        '''
        user = get_user_model().cached_fetch(user_id)
        if user is None:
            user_response = user_api.get_user(user_id)
            user = get_user_model()()
            user.update_response_fields(user_response)
            user.save()
        return user

# pylint: disable=unused-argument
    def has_perm(self, user_obj, perm, obj=None):
        '''
        Does the user have permission to do something
        '''
        return True
