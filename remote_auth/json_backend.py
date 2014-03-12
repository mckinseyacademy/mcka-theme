from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from api_client import api_exec

class JsonBackend(object):
    """
    Authenticate against the remote server using an API call...
    """

    def authenticate(self, username = None, password = None):
        auth_info = api_exec.authenticate(username, password)
        user = get_user_model()()
        user.update_from_auth_response(auth_info)
        return user

    def get_user(self, user_id):
        return None

    def has_perm(self, user_obj, perm, obj = None):
        return True
