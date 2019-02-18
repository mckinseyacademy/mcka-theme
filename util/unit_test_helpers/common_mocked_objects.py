"""
Common mocked objects and methods for writing unit tests in Apros
"""
from mock import patch, Mock

from django.test import RequestFactory, Client

from api_client.group_api import PERMISSION_GROUPS
from accounts.models import RemoteUser
from api_client.api_error import ApiError


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


def make_side_effect_raise_api_error(api_error_code):
    """
    Add this as side-effect to simulate APiError
    """
    thrown_error = Mock()
    thrown_error.code = api_error_code
    thrown_error.reason = "I have no idea, but luckily it is irrelevant for the test"

    def _raise(*args, **kwargs):
        raise ApiError(thrown_error=thrown_error, function_name='irrelevant')

    return _raise


class ApplyPatchMixin(object):
    """
    Mixin with patch helper method
    """

    def apply_patch(self, *args, **kwargs):
        """
        Applies patch and registers a callback to stop the patch in TearDown method
        """
        patcher = patch(*args, **kwargs)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock


class AprosTestingClient(Client):
    """
    Replacement of default client for Apros tests
    provides fake login and role features
    """
    @patch('accounts.json_backend.JsonBackend.authenticate')
    def login(self, mock_auth, user_role=None, **credentials):
        """
        Fakes Apros login with passed user and role
        """
        user = RemoteUser.objects.create_user(
            id=credentials.get('id') or 1,
            username=credentials.get('username') or 'mcka_admin_user',
            email=credentials.get('email') or 'user@example.com'
        )

        role_to_methods = {
            PERMISSION_GROUPS.MCKA_ADMIN: 'is_mcka_admin',
            PERMISSION_GROUPS.MCKA_SUBADMIN: 'is_mcka_subadmin',
            PERMISSION_GROUPS.CLIENT_ADMIN: 'is_client_admin',
            PERMISSION_GROUPS.COMPANY_ADMIN: 'is_company_admin',
            PERMISSION_GROUPS.CLIENT_SUBADMIN: 'is_client_subadmin',
            PERMISSION_GROUPS.MCKA_TA: 'is_mcka_ta',
            PERMISSION_GROUPS.CLIENT_TA: 'is_client_ta',
            PERMISSION_GROUPS.INTERNAL_ADMIN: 'is_internal_admin',
            PERMISSION_GROUPS.MANAGER: 'is_manager',
        }

        for role, prop in role_to_methods.items():
            setattr(user, prop, user_role == role)

        def is_user_in_group(user, *group_names):
            return user_role in group_names

        mock_perm = patch('lib.authorization.is_user_in_permission_group').start()
        mock_perm.side_effect = is_user_in_group

        mock_auth.return_value = user
        self.force_login(user)

        return True
