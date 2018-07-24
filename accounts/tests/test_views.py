import urllib2
import uuid

import ddt
import mock
import requests
from django.conf import settings
from django.http import HttpResponse, SimpleCookie
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from django.utils import translation
from mock import Mock, patch

from accounts.controller import ProcessAccessKeyResult
from accounts.models import RemoteUser
from accounts.tests.utils import ApplyPatchMixin, make_user
from accounts.views import (MISSING_ACCESS_KEY_ERROR, MOBILE_URL_SCHEME_COOKIE, _build_mobile_redirect_response,
                            _cleanup_username as cleanup_username, access_key, finalize_sso_mobile, sso_error,
                            sso_finalize, sso_launch, switch_language_based_on_preference, get_username_for_login_id)
from admin.models import AccessKey, ClientCustomization
from api_client.api_error import ApiError
from util.i18n_helpers import set_language


class AccessLandingTests(TestCase, ApplyPatchMixin):
    """
    Test view for handling invitation URLs
    """

    def setUp(self):
        super(AccessLandingTests, self).setUp()
        self.factory = RequestFactory()
        self.apply_patch('django_assets.templatetags.assets.AssetsNode.render', return_value='')
        self.mock_client = Mock(display_name='TestCo')
        self.apply_patch('api_client.organization_api.fetch_organization', return_value=self.mock_client)
        self.apply_patch('accounts.views._get_redirect_to_current_course', return_value='/protected_home')

    def test_enrolls_authenticated_user(self):
        user_api = self.apply_patch('accounts.controller.user_api')
        user_api.get_user_organizations.return_value = []

        AccessKey.objects.create(client_id=100, code=1234)
        request = self.factory.get('/access/1234')
        request.user = RemoteUser.objects.create_user(username='johndoe', email='john@doe.org', password='password')
        request.session = Mock(session_key='', __contains__=lambda _a, _b: False)

        self.apply_patch('accounts.views.set_current_course_for_user')
        patched_add_message = self.apply_patch('accounts.views.messages.add_message')
        patched_add_message.return_value = []

        response = access_key(request, 1234)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.mock_client.add_user.called)

    def test_switches_current_course_for_authenticated_user(self):
        user_api = self.apply_patch('accounts.controller.user_api')
        user_api.get_user_organizations.return_value = []

        course_id = 'course_id'
        AccessKey.objects.create(client_id=100, code=456, program_id=1, course_id=course_id)
        request = self.factory.get('/access/1234')
        request.user = RemoteUser.objects.create_user(username='johndoe', email='john@doe.org', password='password')
        request.session = Mock(session_key='', __contains__=lambda _a, _b: False)

        patched_set_current_course = self.apply_patch('accounts.views.set_current_course_for_user')
        patched_process_access_key = self.apply_patch('accounts.views.process_access_key')
        patched_process_access_key.return_value = ProcessAccessKeyResult([course_id], ['irrelevant'], [])

        access_key(request, 456)
        patched_set_current_course.assert_called_once_with(request, course_id)

    def test_switches_current_course_for_non_authenticated_user(self):
        user_api = self.apply_patch('accounts.controller.user_api')
        user_api.get_user_organizations.return_value = []

        course_id = 'course_id'
        AccessKey.objects.create(client_id=100, code=456, program_id=1, course_id=course_id)
        request = self.factory.get('/access/1234')
        request.user = Mock()
        request.session = Mock(session_key='', __contains__=lambda _a, _b: False)

        patched_set_current_course = self.apply_patch('accounts.views.set_current_course_for_user')
        patched_process_access_key = self.apply_patch('accounts.views.process_access_key')
        patched_process_access_key.return_value = ProcessAccessKeyResult([course_id], ['irrelevant'], [])

        access_key(request, 456)
        patched_set_current_course.assert_called_once_with(request, course_id)

    def test_missing_access_key(self):
        response = self.client.get('/access/1234')
        self.assertEqual(response.status_code, 404)

    def test_missing_customization(self):
        AccessKey.objects.create(client_id=100, code=1234)
        response = self.client.get('/access/1234')
        self.assertEqual(response.status_code, 404)

    def test_missing_identity_provider(self):
        AccessKey.objects.create(client_id=100, code=1234)
        ClientCustomization.objects.create(client_id=100, identity_provider='')
        response = self.client.get('/access/1234')
        self.assertEqual(response.status_code, 404)

    def test_user_redirected(self):
        AccessKey.objects.create(client_id=100, code=1234)
        ClientCustomization.objects.create(client_id=100, identity_provider='testshib')
        response = self.client.get('/access/1234')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['redirect_to'].startswith('/auth/login/tpa-saml/?'))


@ddt.ddt
class TestUsernameCleanup(TestCase, ApplyPatchMixin):
    """
    Test the _cleanup_username() method in views.py used during SSO logins.
    """

    def setUp(self):
        super(TestUsernameCleanup, self).setUp()
        self.apply_patch('api_client.user_api.get_users', self.mocked_get_users)

    @staticmethod
    def mocked_get_users(username):
        """ Mock version of user_api.get_users(...) """
        existing_users = ["bob", "cathy", "leader"] + ["leader{}".format(i) for i in range(1, 8)]
        if type(username) is not list:
            username = [username]
        return [Mock() for name in username if name in existing_users]

    @ddt.data(
        # Input, expected output
        ("alice", "alice"),
        ("Alice Smith", "Alice_Smith"),
        ("@lice_Smith!'; DROP TABLE auth_users; --", "lice_Smith_DROP_TABLE_auth_users_--"),
        ("bob", "bob1"),
        ("cathy!!!", "cathy1"),
        ("leader", "leader8"),
    )
    @ddt.unpack
    def test_username_cleanup(self, username, expected):
        result = cleanup_username(username)
        self.assertEqual(result, expected)


# TODO: mock API to fix test and uncomment
# class SsoLoginTest(TestCase, ApplyPatchMixin):
#     def setUp(self):
#         super(SsoLoginTest, self).setUp()
#         self.apply_patch('django_assets.templatetags.assets.AssetsNode.render', return_value='')
#
#     def test_no_provider(self):
#         """
#         Users without SSO should end up back at the normal login form.
#         """
#         response = self.client.post(reverse('login'), {
#             'sso_login_form_marker': '',
#             'email': 'foo@bar.com',
#         })
#         self.assertTrue(response.context['error'])
#         self.assertEqual(self.client.cookies['login_mode'].value, 'normal')


@ddt.ddt
class SsoUserFinalizationTests(TestCase, ApplyPatchMixin):
    """
    Test 'finalizing' (registering) user's account when they sign up with SSO
    using an access key.
    """
    SAMPLE_REQUEST_URL = (
        '/accounts/finalize/?data='
        '&hmac=GHA2kEmdlxdgjmWbmAK4oa6bVxIJD3U755CyTO%2B1i%2FI%3D'
    )
    # SAMPLE_SSO_DATA: Example of what gets POSTed to /accounts/finalize/
    # Recorded from the TestShib SAML IdP, using the "myself" user.
    # The shared secret used was the default one in settings.py
    SAMPLE_SSO_POST_DATA = {
        'sso_data': (
            'eyJ1c2VyX2RldGFpbHMiOiB7InVzZXJuYW1lIjogIm15c2VsZiIsICJmdWxsbmFtZSI6ICJNZSBNeXNlbG'
            'YgQW5kIEkiLCAibGFzdF9uYW1lIjogIkFuZCBJIiwgImZpcnN0X25hbWUiOiAiTWUgTXlzZWxmIiwgImVt'
            'YWlsIjogIm15c2VsZkB0ZXN0c2hpYi5vcmcifSwgInByb3ZpZGVyX2lkIjogInNhbWwtdGVzdHNoaWIiLC'
            'AiYXV0aF9lbnRyeSI6ICJhcHJvcyIsICJiYWNrZW5kX25hbWUiOiAidHBhLXNhbWwifQ=='
        ),
        'sso_data_hmac': 'omhQTNK20h6SnPiRnpz8mWdPxmQH02heTS4J5eTxQYE=',
    }

    def make_raise_exception_side_effect(self, exception):
        def func(*unusued_args, **unusued_kwargs):
            raise exception

        return func

    def setUp(self):
        super(SsoUserFinalizationTests, self).setUp()
        # Since we're not logged in for these tests, we must manually create a test client session:
        self.client.cookies['sessionid'] = 'test_lms_session_id'
        self.client_id = 100
        self.access_key = AccessKey.objects.create(client_id=self.client_id, code=uuid.uuid4())
        ClientCustomization.objects.create(client_id=self.client_id, identity_provider='testshib')
        self.apply_patch('api_client.organization_api.fetch_organization', return_value=Mock(display_name='TestCo'))
        self.get_users_patch = self.apply_patch('api_client.user_api.get_users', return_value=[])
        self.apply_patch('django_assets.templatetags.assets.AssetsNode.render', return_value='')

    @patch('api_client.user_api.register_user')
    @patch('django.contrib.auth.login')
    @ddt.data(True, False)
    def test_sso_flow(self, with_existing_user, mock_login, mock_register_user):
        if with_existing_user:
            # Mock to simulate a user named 'myself' already existing on the system:
            self.get_users_patch.side_effect = lambda username: [Mock()] if username == "myself" else []
        # Start with an access code:
        response = self.client.get('/access/{}'.format(self.access_key.code))
        self.assertEqual(response.status_code, 200)
        # That will then redirect us to the SSO provider...
        self.assertTrue(response.context['redirect_to'].startswith('/auth/login/tpa-saml/?'))

        # The user then logs in and gets redirected back to Apros:
        response = self.client.post('/accounts/finalize/', data=self.SAMPLE_SSO_POST_DATA)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/accounts/sso_reg/')

        # The form is bypassed completely, and the user gets redirected to the LMS then the
        # apros dashboard.

        with patch('courses.user_courses.set_current_course_for_user'), \
             patch('os.urandom', return_value='0000'), \
             patch('django.contrib.auth.authenticate'), \
             patch('accounts.views._process_access_key_and_remove_from_session'):
            response = self.client.get(response['Location'])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/auth/complete/tpa-saml/')

        # Then the user should be registered:
        expected_username = u'myself' if not with_existing_user else u'myself1'
        mock_register_user.assert_called_once_with({
            'username': expected_username,
            'city': u'New York',
            'title': u'',
            'country': u'',
            'company': u'TestCo',
            'is_active': True,
            'full_name': u'Me Myself And I',
            'accept_terms': True,
            'password': 'MDAwMA==',
            'email': u'myself@testshib.org',
        })

    def test_sso_missing_access_key(self):
        # The user arrives at reg finalization form without access key in session:
        response = self.client.post('/accounts/finalize/', data=self.SAMPLE_SSO_POST_DATA)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/accounts/sso_error/')
        session = self.client.session

        self.assertIn('sso_error_details', session)
        self.assertEqual(session['sso_error_details'], MISSING_ACCESS_KEY_ERROR)

    def test_existing_user_account_conflict(self):
        # setting up access key id in session
        response = self.client.get('/access/{}'.format(self.access_key.code))
        self.assertEqual(response.status_code, 200)

        # Setting up provider_data in session
        response = self.client.post('/accounts/finalize/', data=self.SAMPLE_SSO_POST_DATA)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/accounts/sso_reg/')

        error_reason = "Duplicate user"
        http_error = urllib2.HTTPError("http://irrelevant", 404, error_reason, None, None)
        api_error = ApiError(http_error, "create_user", None)

        with mock.patch('accounts.views.user_api') as user_api_mock:
            user_api_mock.register_user.side_effect = self.make_raise_exception_side_effect(api_error)
            self.client.session['provider_data'] = {
                'username': 'myself',
                'full_name': 'Me Myself And I',
                'email': 'myself@testshib.org',
                'city': 'Mogadishu',
                'accept_terms': True
            }

            response = self.client.post('/accounts/sso_reg/')

        self.assertIn('error_details', response.context)
        self.assertIn(error_reason, response.context['error_details'])
        self.assertIn('Failed to register user', response.context['error_details'])


@ddt.ddt
class GoogleAnalyticsTest(TestCase):
    """
    Tests that we try to load Google Analytics loads for all IP addresses.
    """

    @ddt.data(
        ('8.8.8.8', True),  # US Google Servers
        ('202.46.33.58', True),  # Chinese DNS Server
    )
    @ddt.unpack
    def test_google_analytics_on_homepage_with_different_origination(
        self,
        ip_address,
        google_analytics_should_be_present
    ):
        response = self.client.get('/', REMOTE_ADDR=ip_address, HTTP_X_FORWARDED_FOR=ip_address)
        rendered = response.content

        if google_analytics_should_be_present:
            self.assertIn('google-analytics.com', rendered)
        else:
            self.assertNotIn('google-analytics.com', rendered)


@ddt.ddt
class TestSwitchLanguageBasedOnPreference(TestCase, ApplyPatchMixin):

    def setUp(self):
        self.factory = RequestFactory()
        self.get_current_request = self.apply_patch('util.i18n_helpers.get_current_request')

    def _populate_dummy_request(self, url):
        request = self.factory.get(url)
        request.META['HTTP_REFERER'] = url
        request.LANGUAGE_CODE = 'gb'
        request.session = {}
        return request

    @ddt.data(
        ('https://apros.mcka.local/terms?LANG=ar', 'ar'),
        ('https://apros.mcka.local?LANG=en', 'en'),
        ('http://www.mckisneyacademy.com/privacy?LANG=ar', 'ar')
    )
    @ddt.unpack
    def test_with_valid_language_input(self, url, expected_language):
        request = self._populate_dummy_request(url)
        self.get_current_request.return_value = request
        response = switch_language_based_on_preference(request)
        self.assertEquals(expected_language, response.cookies['preferred_language'].value)
        self.assertEquals(expected_language, request.session[translation.LANGUAGE_SESSION_KEY])

    @ddt.data(
        ('https://apros.mcka.local/terms?LANG=hb', 'en'),
        ('https://apros.mcka.local', 'en'),
        ('http://www.mckisneyacademy.com/privacy?LANG=lr', 'en')
    )
    @ddt.unpack
    def test_with_invalid_language(self, url, expected_language):
        request = self._populate_dummy_request(url)
        self.get_current_request.return_value = request
        response = switch_language_based_on_preference(request)
        self.assertEquals(None, response.cookies.get('preferred_language'))
        self.assertEquals(expected_language, request.session[translation.LANGUAGE_SESSION_KEY])

    def tearDown(self):
        set_language('en-us')



@ddt.ddt
class TestMobileSSOApi(TestCase, ApplyPatchMixin):

    def setUp(self):
        self.factory = RequestFactory()

    def _setup_request(self, request, user=None, sessionid=''):
        request.user = user
        request.session = Mock(session_key=sessionid, __contains__=lambda _a, _b: False)

    def test_built_mobile_redirect_response(self):
        request = self.factory.get('/')
        self._setup_request(request)
        request.COOKIES[MOBILE_URL_SCHEME_COOKIE] = 'test-scheme'
        redirect_path = 'test-scheme://{}?test=data&more=data'.format(settings.MOBILE_SSO_PATH)
        response = _build_mobile_redirect_response(request, {'test': 'data', 'more': 'data'})
        self.assertIn(redirect_path, response.content)

    @ddt.data(None, 'providerid')
    def test_sso_launch_invalid_provider_id(self, provider_id):
        request = self.factory.get('/accounts/sso_launch/', {'provider_id': provider_id})
        self._setup_request(request)
        response = sso_launch(request)
        self.assertEqual('{"error": "invalid_provider_id"}', response.content)

    @ddt.data(None, 'providerid')
    def test_sso_launch_invalid_provider_id_mobile(self, provider_id):
        request = self.factory.get('/accounts/sso_launch/', {
            'provider_id': provider_id,
            'mobile_url_scheme': 'test-scheme',
        })
        self._setup_request(request)
        response = sso_launch(request)
        self.assertIn('?error=invalid_provider_id', response.content)

    @patch('accounts.views._build_sso_redirect_url')
    def test_sso_launch_valid_provider_id(self, mock__build_sso_redirect_url):
        request = self.factory.get('/accounts/sso_launch/', {
            'provider_id': 'saml-test',
            'mobile_url_scheme': 'test-scheme',
        })
        self._setup_request(request)
        response = sso_launch(request)
        mock__build_sso_redirect_url.assert_called_with('test', '/accounts/finalize/')

    def test_finalize_sso_mobile_error(self):
        request = self.factory.get('/accounts/finalize/', {'error': 'test-error'})
        self._setup_request(request)
        request.COOKIES[MOBILE_URL_SCHEME_COOKIE] = 'test-scheme'
        response = finalize_sso_mobile(request)
        self.assertIn('?error=test-error', response.content)

    def test_finalize_sso_mobile_authorize_step(self):
        request = self.factory.get('/accounts/finalize/')
        self._setup_request(request)
        request.COOKIES[MOBILE_URL_SCHEME_COOKIE] = 'test-scheme'
        response = finalize_sso_mobile(request)
        self.assertEqual(302, response.status_code)
        self.assertIn('/oauth2/authorize/', response.url)

    @ddt.data(
        (requests.ConnectionError, 'connection_error'),
        (requests.HTTPError, 'server_error'),
        (ValueError, 'server_error'),
    )
    @ddt.unpack
    def test_finalize_sso_mobile_access_token_step_error(self, error_class, error_message):
        mock_post = self.apply_patch('accounts.views.requests.post')
        mock_post.side_effect = error_class
        request = self.factory.get('/accounts/finalize/', {'code': 'some-code'})
        self._setup_request(request)
        request.COOKIES[MOBILE_URL_SCHEME_COOKIE] = 'test-scheme'
        response = finalize_sso_mobile(request)
        self.assertIn('?error={}'.format(error_message), response.content)

    def test_finalize_sso_mobile_access_token_step_error_500(self):
        mock_post = self.apply_patch('accounts.views.requests.post')
        mock_response = Mock()
        mock_response.status_code = 555
        mock_response.raise_for_status = Mock(side_effect=requests.HTTPError)
        mock_post.return_value = mock_response
        request = self.factory.get('/accounts/finalize/', {'code': 'some-code'})
        self._setup_request(request)
        request.COOKIES[MOBILE_URL_SCHEME_COOKIE] = 'test-scheme'
        response = finalize_sso_mobile(request)
        self.assertIn('?error=server_error', response.content)

    def test_finalize_sso_mobile_access_token_step_success(self):
        mock_post = self.apply_patch('accounts.views.requests.post')
        mock_response = Mock()
        mock_response.status_code = 333
        mock_response.json = Mock()
        mock_response.json.return_value = {
            'access_token': 'some-token'
        }
        mock_post.return_value = mock_response
        request = self.factory.get('/accounts/finalize/', {'code': 'some-code'})
        self._setup_request(request)
        request.COOKIES[MOBILE_URL_SCHEME_COOKIE] = 'test-scheme'
        response = finalize_sso_mobile(request)
        self.assertIn('?access_token=some-token', response.content)

    def test_sso_finalize_uses_mobile_route(self):
        mock_finalize_sso_mobile = self.apply_patch('accounts.views.finalize_sso_mobile')
        request = self.factory.get('/accounts/finalize/')
        self._setup_request(request)
        request.COOKIES[MOBILE_URL_SCHEME_COOKIE] = 'test-scheme'
        response = sso_finalize(request)
        mock_finalize_sso_mobile.assert_called_with(request)

    def test_sso_finalize_uses_normal_route_authenticated(self):
        mock_finalize_sso_registration = self.apply_patch('accounts.views.finalize_sso_registration')
        request = self.factory.get('/accounts/finalize/')
        mock_user = Mock()
        mock_user.is_authenticated = lambda: True
        self._setup_request(request, user=mock_user)
        response = sso_finalize(request)
        self.assertEqual('/home', response.url)
        self.assertEqual(302, response.status_code)

    def test_sso_finalize_uses_normal_route_unauthenticated(self):
        mock_finalize_sso_registration = self.apply_patch('accounts.views.finalize_sso_registration')
        request = self.factory.get('/accounts/finalize/')
        mock_user = Mock()
        mock_user.is_authenticated = lambda: False
        self._setup_request(request, user=mock_user)
        response = sso_finalize(request)
        mock_finalize_sso_registration.assert_called_with(request)

    def test_sso_error_mobile(self):
        request = self.factory.get('/accounts/sso_error/')
        self._setup_request(request)
        request.COOKIES[MOBILE_URL_SCHEME_COOKIE] = 'test-scheme'
        request.session.get = lambda val: 'test-error' if val == 'error' else None
        response = sso_error(request)
        self.assertIn('?error=test-error', response.content)


@ddt.ddt
class LoginViewTest(TestCase, ApplyPatchMixin):
    """
    Tests for the login view
    """

    @patch('accounts.views.user_api.get_users')
    @ddt.data(
        ('testuser', 'username', 'testuser'),
        ('testuser@example.com', 'email', 'testuser'),
    )
    @ddt.unpack
    def test_get_username_for_login_id(self, login_id, id_type, username, mock_get_user):
        user_mock = Mock()
        user_mock.username = username
        mock_get_user.return_value = [user_mock]
        result = get_username_for_login_id(login_id)
        mock_get_user.assert_called_with(**{id_type: login_id})
        self.assertEqual(result, username)

    def test_login_redirects_for_ie(self):
        host = 'apros.mcka.local'
        response = self.client.get('/accounts/login/',
                                   HTTP_HOST=host,
                                   HTTP_USER_AGENT='Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)')
        self.assertRedirects(response, 'http://{}/'.format(host))

    def test_login_account_activate_check(self):
        response = self.client.get('/accounts/login/', {'account_activate_check': True})
        self.assertIn(
            "Your account has already been activated. Please enter credentials to login",
            response.content)

    @ddt.unpack
    @ddt.data(
        ('done', 'Password Reset Successful'),
        ('complete', 'Password Reset Complete'),
        ('failed', 'Password Reset Unsuccessful'),
    )
    def test_login_account_reset(self, reset_code, reset_message):
        response = self.client.get('/accounts/login/', {'reset': reset_code})
        self.assertIn(reset_message, response.content)

    @patch('django.contrib.auth.authenticate')
    def test_login_with_session_id_error(self, mock_authenticate):
        error_reason = "Error eb764978-01aa-40dd-beae-e942ba761641"
        http_error = urllib2.HTTPError("http://irrelevant", 409, error_reason, None, None)
        mock_authenticate.side_effect = ApiError(http_error, "get_session", None)
        self.client.cookies = SimpleCookie({'sessionid': 'test-session-id'})
        response = self.client.get('/accounts/login/')
        self.assertIn(error_reason, response.content)

    @patch('django.contrib.auth.authenticate')
    def test_login_with_session_id_no_user(self, mock_authenticate):
        self.client.cookies = SimpleCookie({'sessionid': 'test-session-id'})
        response = self.client.get('/accounts/login/')
        self.assertTemplateUsed(response, 'accounts/login.haml')

    @patch('django.contrib.auth.login')
    @patch('accounts.views.append_user_mobile_app_id_cookie')
    @patch('django.contrib.auth.authenticate')
    def test_login_with_session_id_no_user(self, mock_authenticate, mock_1, mock_2):
        mock_authenticate.return_value = make_user()
        self.client.cookies = SimpleCookie({'sessionid': 'test-session-id'})
        response = self.client.get('/accounts/login/', {'next': '/'})
        self.assertRedirects(response, '/')

    @patch('accounts.views.get_sso_provider')
    @patch('accounts.views.get_username_for_login_id')
    @patch('accounts.views.auth.authenticate')
    @ddt.data('test', 'test@email.com')
    def test_login_validate_invalid_login_id(self, login_id, mock_authenticate, mock_get_username,
                                               mock_get_sso_provider):
        mock_get_sso_provider.return_value = None
        mock_authenticate.return_value = None
        mock_get_username.return_value = None
        response = self.client.post('/accounts/login/', {'login_id': login_id, 'validate_login_id': True})
        self.assertIn("Username/email is not recognised. Try again.", response.content)

    @patch('accounts.views.get_sso_provider')
    @patch('accounts.views.get_username_for_login_id')
    @ddt.data('test', 'test@email.com')
    def test_login_validate_valid_login_id(self, login_id, mock_get_username, mock_get_sso_provider):
        mock_get_sso_provider.return_value = None
        mock_get_username.return_value = 'test'
        response = self.client.post('/accounts/login/', {'login_id': login_id, 'validate_login_id': True})
        self.assertIn('{"login_id": "valid"}', response.content)

    @patch('accounts.views.get_sso_provider')
    def test_login_validate_error(self, mock_get_sso_provider):
        error_reason = "Error adccbfc7-33eb-484b-a917-b7d65a5d72f8"
        http_error = urllib2.HTTPError("http://irrelevant", 409, error_reason, None, None)
        mock_get_sso_provider.side_effect = ApiError(http_error, "get_provider", None)
        response = self.client.post('/accounts/login/', {'login_id': 'test@email.com', 'validate_login_id': True})
        self.assertIn('{"error": "%s"}' % error_reason, response.content)

    @patch('accounts.views._build_sso_redirect_url')
    @patch('accounts.views.get_sso_provider')
    @ddt.data('test', 'test@email.com')
    def test_login_validate_sso_user(self, login_id, mock_get_sso_provider, mock_build_sso_redirect):
        mock_get_sso_provider.return_value = 'saml-testprovider'
        mock_build_sso_redirect.return_value = '/'
        response = self.client.post('/accounts/login/', {'login_id': login_id, 'validate_login_id': True})
        self.assertRedirects(response, '/')

    @patch('accounts.views.get_username_for_login_id')
    def test_login_normal_error(self, mock_get_username):
        error_reason = "Error adccbfc7-33eb-484b-a917-b7d65a5d72f8"
        http_error = urllib2.HTTPError("http://irrelevant", 409, error_reason, None, None)
        mock_get_username.side_effect = ApiError(http_error, "get_session", None)
        response = self.client.post('/accounts/login/', {'login_id': 'test', 'password': 'password'})
        self.assertIn(error_reason, response.content)

    @patch('accounts.views.get_username_for_login_id')
    @patch('accounts.views.auth.authenticate')
    @ddt.data('johndoe', 'john@doe.org')
    def test_login_normal_invalid_password(self, login_id, mock_authenticate, mock_get_username):
        mock_get_username.return_value = 'test'
        mock_authenticate.return_value = None
        response = self.client.post('/accounts/login/', {'login_id': login_id, 'password': 'password'})
        self.assertIn('{"password": "Password doesn\'t match our records. Try again."}', response.content)

    @patch('accounts.views._process_authenticated_user')
    @patch('accounts.views.get_username_for_login_id')
    @patch('accounts.views.auth.authenticate')
    @ddt.data('johndoe', 'john@doe.org')
    def test_login_normal_success(self, login_id, mock_authenticate, mock_get_username,
                                    mock__process_authenticated_user):
        self.apply_patch('accounts.views._append_login_mode_cookie')
        self.apply_patch('accounts.views.append_user_mobile_app_id_cookie')
        response_msg = "Test response ab7f8814-e84d-4bd5-a665-573285dc499f"
        mock__process_authenticated_user.return_value = HttpResponse(response_msg)
        mock_get_username.return_value = 'test'
        mock_authenticate.return_value = make_user()
        response = self.client.post('/accounts/login/', {'login_id': login_id, 'password': 'password'})
        self.assertIn(response_msg, response.content)