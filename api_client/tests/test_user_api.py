from cStringIO import StringIO

from django.test import TestCase
from django.conf import settings
from mock import patch

from api_client import user_api


class UserApiTest(TestCase):
    @patch('api_client.user_api.DELETE')
    def test_delete_users_by_username(self, mock_delete):
        mock_delete.side_effect = lambda _: StringIO('{}')
        user_api.delete_users(username='edx')
        mock_delete.assert_called_with('{}/{}?username=edx'.format(settings.API_SERVER_ADDRESS, user_api.USER_API))
        mock_delete.reset_mock()

        # username takes precedence
        user_api.delete_users(username='edx', ids=[1, 2, 3])
        mock_delete.assert_called_with('{}/{}?username=edx'.format(settings.API_SERVER_ADDRESS, user_api.USER_API))

    @patch('api_client.user_api.DELETE')
    def test_delete_users_by_ids(self, mock_delete):
        mock_delete.side_effect = lambda _: StringIO('{}')
        user_api.delete_users(ids=[1, 2, 3])
        mock_delete.assert_called_with('{}/{}?ids=1%2C2%2C3'.format(settings.API_SERVER_ADDRESS, user_api.USER_API))

    def test_delete_users_missing_args(self):
        self.assertRaises(ValueError, user_api.delete_users)
