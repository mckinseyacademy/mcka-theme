from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from api_client import api_exec


class JsonBackend(object):

    """
    Authenticate against the remote server using an API call...
    """

    def authenticate(self, username=None, password=None):
        auth_info = api_exec.authenticate(username, password)
        user = get_user_model()()
        user.update_response_fields(auth_info.user, auth_info.token)
        user.save()
        return user

    def get_user(self, user_id):
        user = get_user_model().cached_fetch(user_id)
        if None == user:
            user_response = api_exec.get_user(user_id)
            user = get_user_model()()
            user.update_response_fields(user_response)
            user.save()
        return user

    def has_perm(self, user_obj, perm, obj=None):
        return True
