# -*- coding: utf-8 -*-
import urllib.request
import urllib.error
import urllib.parse
import uuid
from urllib.parse import urlencode
from urllib.parse import urlparse, parse_qs

import ddt
import mock
import requests
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http import HttpResponse, SimpleCookie
from django.test import RequestFactory, TestCase
from django.utils import translation
from mock import Mock, patch
from rest_framework import status

from accounts.controller import ProcessAccessKeyResult
from accounts.models import RemoteUser
from accounts.tests.utils import ApplyPatchMixin, make_user, AccessKeyTestBase
from accounts.views import (MISSING_ACCESS_KEY_ERROR, MOBILE_URL_SCHEME_COOKIE, _build_mobile_redirect_response,
                            _cleanup_username as cleanup_username, access_key, finalize_sso_mobile, sso_error,
                            sso_finalize, sso_launch, switch_language_based_on_preference, get_user_from_login_id,
                            fill_email_and_redirect, _build_sso_redirect_url)
from admin.models import AccessKey, ClientCustomization
from api_client.api_error import ApiError
from lib.utils import DottableDict
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
            self.get_users_patch.side_effect = lambda username: [Mock()] if username == "Me_Myself_And_I" else []
        # Start with an access code:
        response = self.client.get('/access/{}'.format(self.access_key.code))
        self.assertEqual(response.status_code, 200)
        # That will then redirect us to the SSO provider...
        self.assertTrue(response.context['redirect_to'].startswith('/auth/login/tpa-saml/?'))

        # The user then logs in and gets redirected back to Apros:
        response = self.client.post('/accounts/finalize/', data=self.SAMPLE_SSO_POST_DATA)
        self.assertEqual(response.status_code, 302)

        url = response['Location']
        self.assertTrue(url.endswith('/accounts/sso_reg/'))

        with patch('courses.user_courses.set_current_course_for_user'), \
                patch('accounts.views.get_random_string', return_value='0000'), \
                patch('django.contrib.auth.authenticate'), \
                patch('accounts.views._process_access_key_and_remove_from_session'):
            response = self.client.get(url)
            # The user should see the terms of service for new users.
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'accounts/sso_terms_of_service.haml')
            response = self.client.post(url, {'accept_terms': True})
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response['Location'].endswith('/auth/complete/tpa-saml/'))

        # Then the user should be registered:
        expected_username = 'Me_Myself_And_I' if not with_existing_user else 'Me_Myself_And_I1'
        mock_register_user.assert_called_once_with({
            'username': expected_username,
            'city': 'New York',
            'title': '',
            'country': '',
            'company': 'TestCo',
            'is_active': True,
            'full_name': 'Me Myself And I',
            'accept_terms': True,
            'password': 'MDAwMA==',
            'email': 'myself@testshib.org',
        })

    def test_sso_missing_access_key(self):
        # The user arrives at reg finalization form without access key in session:
        response = self.client.post('/accounts/finalize/', data=self.SAMPLE_SSO_POST_DATA)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/sso_error/')
        session = self.client.session

        self.assertIn('sso_error_details', session)
        self.assertEqual(session['sso_error_details'], MISSING_ACCESS_KEY_ERROR)

    def test_existing_user_account_conflict(self):
        # setting up access key id in session
        response = self.client.get('/access/{}'.format(self.access_key.code))
        self.assertEqual(response.status_code, 200)

        # Setting up provider_data in session
        # import pdb;pdb.set_trace()
        response = self.client.post('/accounts/finalize/', data=self.SAMPLE_SSO_POST_DATA)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/sso_reg/')

        error_reason = "Duplicate user"
        http_error = urllib.error.HTTPError("http://irrelevant", 404, error_reason, None, None)
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

            response = self.client.post('/accounts/sso_reg/', {'accept_terms': True})

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
        rendered = response.content.decode('utf-8')

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
        self.assertEqual(expected_language, response.cookies['preferred_language'].value)
        self.assertEqual(expected_language, request.session[translation.LANGUAGE_SESSION_KEY])

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
        self.assertEqual(None, response.cookies.get('preferred_language'))
        self.assertEqual(expected_language, request.session[translation.LANGUAGE_SESSION_KEY])

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
        data = {'test': 'data', 'more': 'data'}
        redirect_path = 'test-scheme://{}?{}'.format(settings.MOBILE_SSO_PATH, urlencode(data))
        response = _build_mobile_redirect_response(request, data)
        self.assertIn(redirect_path, response.content.decode('utf-8'))

    @ddt.data(
        ('invalid-scheme', False),
        ('test-scheme', True),
    )
    @ddt.unpack
    def test_built_mobile_url_scheme_validity(self, mobile_url_scheme, expected_result):
        request = self.factory.get('/')
        self._setup_request(request)
        request.COOKIES[MOBILE_URL_SCHEME_COOKIE] = mobile_url_scheme
        data = {'test': 'data', 'more': 'data'}
        redirect_path = '{}://{}?{}'.format(mobile_url_scheme, settings.MOBILE_SSO_PATH, urlencode(data))
        response = _build_mobile_redirect_response(request, data)
        self.assertEqual(redirect_path in response.content.decode('utf-8'), expected_result)

    @ddt.data(None, 'providerid')
    def test_sso_launch_invalid_provider_id(self, provider_id):
        request = self.factory.get('/accounts/sso_launch/', {'provider_id': provider_id})
        self._setup_request(request)
        response = sso_launch(request)
        self.assertEqual('{"error": "invalid_provider_id"}', response.content.decode('utf-8'))

    @ddt.data(None, 'providerid')
    def test_sso_launch_invalid_provider_id_mobile(self, provider_id):
        request = self.factory.get('/accounts/sso_launch/', {
            'provider_id': provider_id,
            'mobile_url_scheme': 'test-scheme',
        })
        self._setup_request(request)
        response = sso_launch(request)
        self.assertIn('?error=invalid_provider_id', response.content.decode('utf-8'))

    @patch('accounts.views._build_sso_redirect_url')
    def test_sso_launch_valid_provider_id(self, mock__build_sso_redirect_url):
        request = self.factory.get('/accounts/sso_launch/', {
            'provider_id': 'saml-test',
            'mobile_url_scheme': 'test-scheme',
        })
        self._setup_request(request)
        sso_launch(request)
        mock__build_sso_redirect_url.assert_called_with('test', '/accounts/finalize/')

    def test_finalize_sso_mobile_login(self):
        """
        Tests that the mobile sso finalization flow initiates an SSO registration
        if initiated for a new user.
        """
        mock_finalize_sso_registration = self.apply_patch('accounts.views.finalize_sso_registration')
        mock_authenticate = self.apply_patch('accounts.views.auth.authenticate')
        mock_authenticate.return_value = None
        request = self.factory.get('/accounts/finalize/')
        request.COOKIES['sessionid'] = 'test-session-id'
        finalize_sso_mobile(request)
        mock_finalize_sso_registration.assert_called_with(request)

    def test_finalize_sso_mobile_error(self):
        request = self.factory.get('/accounts/finalize/', {'error': 'test-error'})
        self._setup_request(request)
        request.COOKIES[MOBILE_URL_SCHEME_COOKIE] = 'test-scheme'
        response = finalize_sso_mobile(request)
        self.assertIn('?error=test-error', response.content.decode('utf-8'))

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
        self.assertIn('?error={}'.format(error_message), response.content.decode('utf-8'))

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
        self.assertIn('?error=server_error', response.content.decode('utf-8'))

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
        self.assertIn('?access_token=some-token', response.content.decode('utf-8'))

    def test_sso_finalize_uses_mobile_route(self):
        mock_finalize_sso_mobile = self.apply_patch('accounts.views.finalize_sso_mobile')
        request = self.factory.get('/accounts/finalize/')
        self._setup_request(request)
        request.COOKIES[MOBILE_URL_SCHEME_COOKIE] = 'test-scheme'
        sso_finalize(request)
        mock_finalize_sso_mobile.assert_called_with(request)

    def test_sso_finalize_uses_normal_route_authenticated(self):
        self.apply_patch('accounts.views.finalize_sso_registration')
        request = self.factory.get('/accounts/finalize/')
        mock_user = Mock()
        mock_user.is_authenticated = True
        self._setup_request(request, user=mock_user)
        response = sso_finalize(request)
        self.assertEqual('/home', response.url)
        self.assertEqual(302, response.status_code)

    def test_sso_finalize_uses_normal_route_unauthenticated(self):
        mock_finalize_sso_registration = self.apply_patch('accounts.views.finalize_sso_registration')
        request = self.factory.get('/accounts/finalize/')
        mock_user = Mock()
        mock_user.is_authenticated = False
        self._setup_request(request, user=mock_user)
        sso_finalize(request)
        mock_finalize_sso_registration.assert_called_with(request)

    def test_sso_error_mobile(self):
        request = self.factory.get('/accounts/sso_error/')
        self._setup_request(request)
        request.COOKIES[MOBILE_URL_SCHEME_COOKIE] = 'test-scheme'
        request.session.get = lambda val: 'test-error' if val == 'error' else None
        response = sso_error(request)
        self.assertIn('?error=test-error', response.content.decode('utf-8'))


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
    def test_get_user_from_login_id(self, login_id, id_type, username, mock_get_user):
        user_mock = Mock()
        user_mock.username = username
        mock_get_user.return_value = [user_mock]
        result = get_user_from_login_id(login_id)
        mock_get_user.assert_called_with(**{id_type: login_id})
        self.assertEqual(result.username, username)

    def test_login_redirects_for_ie(self):
        host = 'apros.mcka.local'
        response = self.client.get(reverse('login'),
                                   HTTP_HOST=host,
                                   HTTP_USER_AGENT='Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)')
        self.assertRedirects(response, 'http://{}/'.format(host))

    def test_login_account_activate_check(self):
        response = self.client.get(reverse('home'), {'account_activate_check': True})
        self.assertIn(
            "Your account has already been activated. Please enter credentials to login",
            response.content.decode('utf-8'))

    @ddt.unpack
    @ddt.data(
        ('done', 'Password Reset Successful'),
        ('complete', 'Password Reset Complete'),
        ('failed', 'Password Reset Unsuccessful'),
    )
    def test_login_account_reset(self, reset_code, reset_message):
        response = self.client.get(reverse('home'), {'reset': reset_code})
        self.assertIn(reset_message, response.content.decode('utf-8'))

    @patch('django.contrib.auth.authenticate')
    def test_login_with_session_id_error(self, mock_authenticate):
        error_reason = "Error eb764978-01aa-40dd-beae-e942ba761641"
        http_error = urllib.error.HTTPError("http://irrelevant", 409, error_reason, None, None)
        mock_authenticate.side_effect = ApiError(http_error, "get_session", None)
        self.client.cookies = SimpleCookie({'sessionid': 'test-session-id'})
        response = self.client.get(reverse('protected_home'))
        self.assertIn(error_reason, response.content.decode('utf-8'))

    @patch('django.contrib.auth.authenticate')
    def test_login_with_session_id_no_user(self, mock_authenticate):
        self.client.cookies = SimpleCookie({'sessionid': 'test-session-id'})
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/landing.haml')

    # TODO fix this ---> redefinition of unused 'test_login_with_session_id_no_user' from line 565
    @patch('django.contrib.auth.login')  # noqa: F811
    @patch('accounts.views.append_user_mobile_app_id_cookie')
    @patch('django.contrib.auth.authenticate')
    def test_login_with_session_id_no_user(self, mock_authenticate, mock_1, mock_2):
        mock_authenticate.return_value = make_user()
        self.client.cookies = SimpleCookie({'sessionid': 'test-session-id'})
        response = self.client.get(reverse('login'), {'next': '/'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    @patch('accounts.views.get_sso_provider')
    @patch('accounts.views.get_user_from_login_id')
    @patch('accounts.views.auth.authenticate')
    @ddt.data('test', 'test@email.com')
    def test_login_validate_invalid_login_id(self, login_id, mock_authenticate, mock_get_username,
                                             mock_get_sso_provider):
        mock_get_sso_provider.return_value = None
        mock_authenticate.return_value = None
        mock_get_username.return_value = DottableDict({"username": None, "is_active": True})
        response = self.client.post(reverse('home'), {'login_id': login_id, 'validate_login_id': True})
        self.assertIn("Username/email is not recognized. Try again.", response.content.decode('utf-8'))

    @patch('accounts.views.get_sso_provider')
    @patch('accounts.views.get_user_from_login_id')
    @patch('accounts.views.auth.authenticate')
    @ddt.data('atestuser', 'atestuser@email.com')
    def test_login_prefill_login_id(self, login_id, mock_authenticate, mock_get_username,
                                    mock_get_sso_provider):
        mock_get_sso_provider.return_value = None
        mock_authenticate.return_value = None
        mock_get_username.return_value = DottableDict({"username": None, "is_active": False})
        response = self.client.get(reverse('home'), {'login_id': login_id})
        self.assertInHTML(
            "<input type='text' name='login_id' value='{login_id}' class='form-control "
            "form-input' id='login_id'>".format(login_id=login_id),
            response.content.decode('utf-8'),
        )

    @patch('accounts.views.get_sso_provider')
    @patch('accounts.views.get_user_from_login_id')
    @ddt.data('test', 'test@email.com')
    def test_login_validate_valid_login_id(self, login_id, mock_get_username, mock_get_sso_provider):
        mock_get_sso_provider.return_value = None
        mock_get_username.return_value = DottableDict({"username": "test", "is_active": True})
        response = self.client.post(reverse('home'), {'login_id': login_id, 'validate_login_id': True})
        self.assertIn('{"login_id": "valid"}', response.content.decode('utf-8'))

    @patch('accounts.views.get_sso_provider')
    def test_login_validate_error(self, mock_get_sso_provider):
        error_reason = "Error adccbfc7-33eb-484b-a917-b7d65a5d72f8"
        http_error = urllib.error.HTTPError("http://irrelevant", 409, error_reason, None, None)
        mock_get_sso_provider.side_effect = ApiError(http_error, "get_provider", None)
        response = self.client.post(reverse('home'), {'login_id': 'test@email.com', 'validate_login_id': True})
        self.assertIn('{"error": "%s"}' % error_reason, response.content.decode('utf-8'))

    @patch('accounts.views._build_sso_redirect_url')
    @patch('accounts.views.get_sso_provider')
    @ddt.data('test', 'test@email.com')
    def test_login_validate_sso_user(self, login_id, mock_get_sso_provider, mock_build_sso_redirect):
        mock_get_sso_provider.return_value = 'saml-testprovider'
        mock_build_sso_redirect.return_value = '/'
        response = self.client.post(reverse('home'), {'login_id': login_id, 'validate_login_id': True})
        self.assertRedirects(response, '/')

    # TODO fix this ---> redefinition of unused 'test_login_validate_sso_user' from line 625
    @patch('accounts.views.get_sso_provider')  # noqa: F811
    @ddt.data('test', 'test@email.com')
    def test_login_validate_sso_user(self, login_id, mock_get_sso_provider):
        """
        Test deep linking when using SSO
        """
        mock_get_sso_provider.return_value = 'saml-testprovider'
        # Set up redirect after login
        post_login_redirect_url = '/some/url'
        login_url_with_next = '{}?{}'.format(reverse('home'), urlencode({'next': post_login_redirect_url}))
        response = self.client.post(login_url_with_next, {'login_id': login_id, 'validate_login_id': True})
        # Ensure that the response will redirect
        self.assertEqual(response.status_code, 302)
        # Get response query params
        parsed_url = urlparse(response['Location'])
        query_params = parse_qs(parsed_url.query)
        # Get query params for post SSO URL
        parsed_redirect_url = urlparse(query_params['next'][0])
        redirect_query_params = parse_qs(parsed_redirect_url.query)
        # Ensue post-SSO-login URL has a next param to redirect to the correct location post-login
        self.assertIn(post_login_redirect_url, redirect_query_params.get('next'))

    @patch('accounts.views.get_user_from_login_id')
    def test_login_normal_error(self, mock_get_username):
        error_reason = "Error adccbfc7-33eb-484b-a917-b7d65a5d72f8"
        http_error = urllib.error.HTTPError("http://irrelevant", 409, error_reason, None, None)
        mock_get_username.side_effect = ApiError(http_error, "get_session", None)
        response = self.client.post(reverse('home'), {'login_id': 'test', 'password': 'password'})
        self.assertIn(error_reason, response.content.decode('utf-8'))

    @patch('accounts.views.get_user_from_login_id')
    @patch('accounts.views.auth.authenticate')
    @ddt.data('johndoe', 'john@doe.org')
    def test_login_normal_invalid_password(self, login_id, mock_authenticate, mock_get_username):
        mock_get_username.return_value = DottableDict({"username": "test", "is_active": True})
        mock_authenticate.return_value = None
        response = self.client.post(reverse('home'), {'login_id': login_id, 'password': 'password'})
        self.assertIn('{"password": "Please enter a valid password."}', response.content.decode('utf-8'))

    @patch('accounts.views.get_user_from_login_id')
    @patch('accounts.views.auth.authenticate')
    @ddt.data('johndoe', 'john@doe.org')
    def test_login_normal_user_lock_out(self, login_id, mock_authenticate,
                                        mock_get_username):
        mock_get_username.return_value = DottableDict({"username": "test", "is_active": True})
        http_error = urllib.error.HTTPError("http://irrelevant", 403, None, None, None)
        mock_authenticate.side_effect = ApiError(http_error, "authenticate", None)
        response = self.client.post(reverse('home'), {'login_id': login_id, 'password': 'password'})
        self.assertIn('{"lock_out": true}', response.content.decode('utf-8'))

    @patch('accounts.views._process_authenticated_user')
    @patch('accounts.views.get_user_from_login_id')
    @patch('accounts.views.auth.authenticate')
    @ddt.data('johndoe', 'john@doe.org')
    def test_login_normal_success(self, login_id, mock_authenticate, mock_get_username,
                                  mock__process_authenticated_user):
        self.apply_patch('accounts.views._append_login_mode_cookie')
        self.apply_patch('accounts.views.append_user_mobile_app_id_cookie')
        response_msg = "Test response ab7f8814-e84d-4bd5-a665-573285dc499f"
        mock__process_authenticated_user.return_value = HttpResponse(response_msg)
        mock_get_username.return_value = DottableDict({"username": "test", "is_active": True})
        mock_authenticate.return_value = make_user()
        response = self.client.post(reverse('home'), {'login_id': login_id, 'password': 'password'})
        self.assertIn(response_msg, response.content.decode('utf-8'))

    @ddt.data('ütest@?', 'ütest@email.com')
    def test_login_validate_with_unicode_email_login_id(self, login_id):
        """
        If we try to post with an invalid data pattern like unicode,
        then it will return the errors and status forbidden.
        """
        response = self.client.post(reverse('home'), {'login_id': login_id, 'password': 'password'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("login_id", response.content.decode('utf-8'))
        self.assertIn("Please enter a valid email containing only English characters and numerals, and the following"
                      " special characters @ . _ -", response.content.decode('utf-8'))

    @ddt.data('ütest?', 'ütestemail.com"')
    def test_login_validate_with_unicode_username_login_id(self, login_id):
        """
        If we try to post with an invalid data pattern like unicode,
        then it will return the errors and status forbidden.
        """
        response = self.client.post(reverse('home'), {'login_id': login_id, 'password': 'password'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("login_id", response.content.decode('utf-8'))
        self.assertIn("Please enter a valid username containing only English characters and numerals, and the "
                      "following special characters _ -", response.content.decode('utf-8'))


@ddt.ddt
class FillEmailRedirectViewTest(TestCase, ApplyPatchMixin):
    """
    Tests for the fill_email_and_redirect view.
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_fill_email_and_redirect_anonymous(self):
        redirect_url = 'http://some.url/?existing=parameter'
        request = self.factory.get(reverse('fill_email_and_redirect', kwargs={
            'redirect_url': redirect_url,
        }))
        request.user = AnonymousUser()
        response = fill_email_and_redirect(request, redirect_url)
        self.assertEqual(response.url, 'http://some.url/?existing=parameter')

    def test_fill_email_and_redirect_authenticated(self):
        redirect_url = 'http://some.url/?existing=parameter'
        request = self.factory.get(reverse('fill_email_and_redirect', kwargs={
            'redirect_url': redirect_url,
        }))
        request.user = Mock()
        request.user.is_anonymous = lambda: False
        request.user.email = 'some@email.org'
        response = fill_email_and_redirect(request, redirect_url)
        self.assertTrue(response.url.startswith('http://some.url/'))
        self.assertIn('existing=parameter', response.url)
        self.assertIn(urlencode({'email': request.user.email}), response.url)


class AccessKeyTest(AccessKeyTestBase):
    """ Tests for Access Key Views. """

    def setUp(self):
        super(AccessKeyTest, self).setUp()
        self.client_id = self.company.id
        self.code = uuid.uuid4()
        self.course_id = 'test-course'
        AccessKey.objects.create(client_id=self.client_id, code=self.code, course_id=self.course_id)
        self.apply_patch(
            'api_client.organization_api.fetch_organization',
            return_value=self.company
        )

    def test_get_invalid_access_key(self):
        """ Test get_access_key with invalid access key """
        response = self.client.get(reverse('access_key_data_api_view', kwargs={'access_key_code': 'ABCDEF'}))
        self.assertEqual(response.status_code, 404)

    def test_missing_client_customization_get_access_key(self):
        """ Test missing ClientCustomization when making a get_access_key request """
        response = self.client.get(reverse('access_key_data_api_view', kwargs={'access_key_code': self.code}))
        self.assertEqual(response.status_code, 404)

    def test_get_valid_access_key(self):
        """ Test get_access_key with valid access key"""
        customization = ClientCustomization.objects.create(client_id=self.client_id, identity_provider='testshib')

        response = self.client.get(reverse('access_key_data_api_view', kwargs={'access_key_code': self.code}))
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['course_id'], self.course_id)
        self.assertEqual(data['organization_id'], self.client_id)
        self.assertEqual(data['provider_id'], customization.identity_provider)

    def test_access_key_mobile_flow(self):
        """ Test access key when a mobile scheme has been provided """
        code = uuid.uuid4()
        identity_provider = 'fake-provider'
        AccessKey.objects.create(client_id=self.client_id, code=code, course_id=self.course_id)
        ClientCustomization.objects.create(client_id=self.client_id, identity_provider=identity_provider)

        url = '{}?mobile_url_scheme=test'.format(reverse('access_key', kwargs=dict(code=code)))

        response = self.client.get(url)
        sso_redirect_url = _build_sso_redirect_url(identity_provider, reverse('sso_finalize'))
        self.assertRedirects(response, sso_redirect_url, fetch_redirect_response=False)


@ddt.ddt
class LogoutnViewTest(TestCase, ApplyPatchMixin):
    """
    Tests for the logout view
    """

    @patch('accounts.logout.user_api.delete_session')
    @ddt.data(
        (None,),
        ('',),
        ('u2uocmbcywqpkx7ats9zd8d4uv0u7ft9',)
    )
    @ddt.unpack
    def test_logout(self, cookie, mock_delete_session):
        mock_delete_session.return_value = []

        self.client.cookies = SimpleCookie({'sessionid': cookie})
        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, '/')
        self.assertEqual('to-delete', response.cookies['csrftoken'].value)
        self.assertEqual('to-delete', response.cookies['sessionid'].value)
