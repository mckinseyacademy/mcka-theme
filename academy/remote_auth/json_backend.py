from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class JsonBackend(object):
    """
    Authenticate against the remote server using an API call...
    """

    def authenticate(self, username = None, password = None):
        session_key = authenticate_with_server(username, password)
        return get_user_model(session_key)

    def get_user(self, user_id):
        return None

    def has_perm(self, user_obj, perm, obj = None):
        return True

    def authenticate_with_server(self, username, password):
        return 'abc123'