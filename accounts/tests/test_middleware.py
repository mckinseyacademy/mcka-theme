import ddt
import urllib.request
import urllib.error
import urllib.parse

from freezegun import freeze_time
from mock import patch, Mock
from datetime import datetime, timedelta

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect

from accounts.middleware.session_timeout import SessionTimeout
from accounts.tests.utils import ApplyPatchMixin
from api_client.api_error import ApiError
from util.unit_test_helpers import AprosTestingClient
from accounts.middleware.thread_local import _threadlocal


@ddt.ddt
class SessionTimeoutTestCase(TestCase, ApplyPatchMixin):
    """ Tests for SessionTimeout middleware"""

    def setUp(self):
        """ Initial setup """
        self.factory = RequestFactory()

    @patch('accounts.middleware.session_timeout.get_user_dict')
    @patch('accounts.middleware.session_timeout.logout')
    def test_session_ok(self, mock_logout, mock_get_user_dict):
        """ Test session is kept unchanged """
        request = self.factory.get(reverse('admin_home'))
        request.user = Mock(is_anonymous=lambda: False)
        request.session = {'last_touch': datetime.utcnow()}

        SessionTimeout(Mock())(request)

        assert 'last_touch' in request.session
        mock_logout.assert_not_called()

    @patch('accounts.middleware.session_timeout.get_user_dict')
    @patch('accounts.middleware.session_timeout.logout')
    def test_session_expired(self, mock_logout, mock_get_user_dict):
        """ Test logout when session timed out """
        request = self.factory.get(reverse('admin_home'))
        request.user = Mock(is_anonymous=lambda: False)
        request.session = {'last_touch': datetime.fromtimestamp(0)}

        SessionTimeout(Mock())(request)

        assert 'last_touch' not in request.session
        mock_logout.assert_called_with(request)

    @patch('accounts.middleware.session_timeout.get_user_dict')
    @patch('accounts.middleware.session_timeout.expire_session')
    def test_user_deleted(self, mock_expire_session, mock_get_user_dict):
        """ Test session expired when user is deleted """
        request = self.factory.get(reverse('admin_home'))
        request.user = Mock(is_anonymous=lambda: False)

        http_error = urllib.error.HTTPError("http://irrelevant", 403, None, None, None)
        mock_get_user_dict.side_effect = ApiError(http_error, "deleted", None)

        SessionTimeout(Mock())(request)

        mock_expire_session.assert_called_with(request)

    @ddt.data(
        datetime.utcnow() + timedelta(days=2),
        datetime.utcnow() + timedelta(days=14),
        datetime.utcnow() + timedelta(days=15),
        datetime.utcnow() + timedelta(days=26),
        datetime.utcnow() + timedelta(days=30),

    )
    @patch('accounts.middleware.session_timeout.get_user_dict')
    @patch('accounts.middleware.session_timeout.logout')
    def test_session_ok_mobile(self, mocked_time, mock_logout, mock_get_user_dict):
        """ Test session is kept unchanged """
        request = self.factory.get(
            reverse('admin_home'),
            HTTP_USER_AGENT='com.mcka.RNApp: <platform>'
        )
        request.user = Mock(is_anonymous=lambda: False)
        request.session = {'last_touch': datetime.utcnow()}

        freezer = freeze_time(mocked_time)
        freezer.start()
        SessionTimeout(Mock())(request)
        freezer.stop()

        assert 'last_touch' in request.session
        mock_logout.assert_not_called()

    @ddt.data(
        datetime.utcnow() + timedelta(days=30, hours=1),
        datetime.utcnow() + timedelta(days=31),
        datetime.utcnow() + timedelta(days=35),
        datetime.utcnow() + timedelta(days=60),
    )
    @patch('accounts.middleware.session_timeout.get_user_dict')
    @patch('accounts.middleware.session_timeout.logout')
    def test_session_expired_mobile(self, mocked_time, mock_logout, mock_get_user_dict):
        """ Test logout when session timed out """
        request = self.factory.get(
            reverse('admin_home'),
            HTTP_USER_AGENT='com.mcka.RNApp: <platform>'
        )
        request.user = Mock(is_anonymous=lambda: False)
        request.session = {'last_touch': datetime.utcnow()}

        freezer = freeze_time(mocked_time)
        freezer.start()
        SessionTimeout(Mock())(request)
        freezer.stop()

        assert 'last_touch' not in request.session
        mock_logout.assert_called_with(request)


class TestAjaxRedirectMiddleware(TestCase):
    client_class = AprosTestingClient

    @patch('accounts.views.public_home')
    def test_ajax_middleware(self, mock_view):
        # ajax request with normal response
        mock_view.return_value = HttpResponse()
        response = self.client.get(path='/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)

        # ajax request with a redirect response
        mock_view.return_value = HttpResponseRedirect(redirect_to='/')
        response = self.client.get(path='/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 278)


class TestThreadLocalMiddleware(TestCase):
        def test_process_request(self):
            # do any arbitrary request
            self.client.get(path='/heartbeat')

            # check if middleware has properly set the data on thread local
            self.assertTrue(
                all([hasattr(_threadlocal, attr)
                    for attr in ['request', 'current_course', 'static_tabs', 'user_permissions']])
            )
