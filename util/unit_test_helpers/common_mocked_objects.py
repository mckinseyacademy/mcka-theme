"""
Common mocked objects and methods for writing unit tests in Apros
"""
from django.test import RequestFactory

from api_client.group_api import PERMISSION_GROUPS


class TestUser(object):
    """
    Represents a minimum User object
    """
    id = None
    email = None

    def __init__(self, user_id, email, username='test_user', is_staff=False, user_role=None):
        """
        the plain, old class initializer
        """
        self.id = user_id
        self.email = email
        self.username = username
        self.is_staff = is_staff
        self.user_role = user_role

    @property
    def is_mcka_admin(self):
        return self.user_role == PERMISSION_GROUPS.MCKA_ADMIN

    @property
    def is_mcka_subadmin(self):
        return self.user_role == PERMISSION_GROUPS.MCKA_SUBADMIN

    @property
    def is_client_admin(self):
        return self.user_role == PERMISSION_GROUPS.CLIENT_ADMIN

    @property
    def is_company_admin(self):
        return self.user_role == PERMISSION_GROUPS.COMPANY_ADMIN

    @property
    def is_internal_admin(self):
        return self.user_role == PERMISSION_GROUPS.INTERNAL_ADMIN


def mock_storage_save(storage_obj, name, content, max_length=None):
    """
    Mocked file storage's `save` method. Only returns path and
    does not write any actual file
    """
    return name


def mock_request_object(path, user=None, **attrs):
    """
    Mocking the actual request to use in test cases
    """
    request = RequestFactory().get(path)

    for attr, val in attrs.iteritems():
        setattr(request, attr, val)

    request.user = user or TestUser(user_id=1, email='user@example.com', username='mcka_admin_user')
    return request
