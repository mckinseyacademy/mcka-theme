from urllib2 import HTTPError

import ddt
import mock

from django.test import TestCase

from accounts.json_backend import JsonBackend
from accounts.tests.utils import ApplyPatchMixin, make_user
from api_client.api_error import ApiError
from api_client.user_models import AuthenticationResponse, UserResponse


@ddt.ddt
class JsonBackendTests(TestCase, ApplyPatchMixin):
    def setUp(self):
        self.backend = JsonBackend()
        self.user_api = self.apply_patch('accounts.json_backend.user_api')

    def _make_auth_response(self, user, token='123'):
        result = mock.Mock(spec=AuthenticationResponse)
        result.user = user
        result.token = token
        return result

    def _make_user_response(self, user):
        if not hasattr(user, 'profile_image'):
            setattr(user, 'profile_image', {
                "image_url_full": "http://test.com/static/images/profiles/default_500.png",
                "image_url_large": "http://test.com/static/images/profiles/default_500.png",
                "image_url_medium": "http://test.com/static/images/profiles/default_160.png",
                "image_url_small": "http://test.com/static/images/profiles/default_48.png",
                "has_image": "false"
            })
        result = UserResponse(dictionary=user.__dict__)
        return result

    def test_authenticate_username_and_password_existing_user(self):
        existing_user = make_user()
        self.user_api.authenticate.return_value = self._make_auth_response(existing_user)
        self.user_api.get_user.return_value = self._make_user_response(existing_user)

        auth_response = self.backend.authenticate(existing_user.username, existing_user.password)
        self.user_api.authenticate.assert_called_once_with(
            existing_user.username, existing_user.password, remote_session_key=None
        )
        self.assertIsNotNone(auth_response)
        self.assertEqual(auth_response.username, existing_user.username)

    @ddt.data(
        ('username', None),
        (None, 'password')
    )
    @ddt.unpack
    def test_authenticate_missing_username_or_password(self, username, password):
        existing_user = make_user(username='username', password='password')
        self.user_api.authenticate.return_value = self._make_auth_response(existing_user)
        self.user_api.get_user.return_value = self._make_user_response(existing_user)

        auth_response = self.backend.authenticate(username, password)
        self.user_api.authenticate.assert_called_once_with(username, password, remote_session_key=None)
        self.assertIsNotNone(auth_response)
        self.assertEqual(auth_response.username, existing_user.username)

    @ddt.data(
        ('key1', ['key1'], False),
        ('key1', ['key2'], True),
    )
    @ddt.unpack
    def test_authenticate_remote_session_key(self, session_key, existing_session_keys, raises):
        existing_user = make_user()

        def _get_session(remote_session_key):
            if remote_session_key not in existing_session_keys:
                http_error = HTTPError("http://irrelevant", 404, "Session not found", None, None)
                raise ApiError(http_error, "get_session", None)
            return mock.Mock(user_id=existing_user.id, token='123')

        self.user_api.authenticate.return_value = self._make_auth_response(existing_user)
        self.user_api.get_session.side_effect = _get_session
        self.user_api.get_user.return_value = self._make_user_response(existing_user)

        auth_response = self.backend.authenticate(remote_session_key=session_key)
        self.user_api.authenticate.assert_not_called()
        if raises:
            self.assertIsNone(auth_response)
        else:
            self.assertIsNotNone(auth_response)
            self.assertEqual(auth_response.username, existing_user.username)

    def test_authenticate_remote_session_key_username_and_password(self):
        existing_user = make_user()

        def _authenticate(username, password, remote_session_key=None):
            if username == existing_user.username and password == existing_user.password:
                return self._make_auth_response(existing_user)
            else:
                http_error = HTTPError("http://irrelevant", 404, "User not found", None, None)
                raise ApiError(http_error, "authenticate", None)

        self.user_api.authenticate.side_effect = _authenticate
        self.user_api.get_user.return_value = self._make_user_response(existing_user)

        auth_response = self.backend.authenticate(
            existing_user.username, existing_user.password, remote_session_key="session_key"
        )
        self.user_api.get_session.assert_not_called()
        self.user_api.authenticate.assert_called_once_with(
            existing_user.username, existing_user.password, remote_session_key="session_key"
        )
        self.assertIsNotNone(auth_response)
        self.assertEqual(auth_response.username, existing_user.username)

    def test_authenticate_remote_session_key_none(self):
        existing_user = make_user()

        self.user_api.authenticate.return_value = self._make_auth_response(existing_user)
        self.user_api.get_session.return_value = mock.Mock(user_id=existing_user.id)
        self.user_api.get_user.return_value = self._make_user_response(existing_user)

        self.backend.authenticate(remote_session_key=None)
        self.user_api.authenticate.assert_called_once_with(None, None, remote_session_key=None)
        self.user_api.get_session.assert_not_called()
