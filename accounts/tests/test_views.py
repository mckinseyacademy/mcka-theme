import uuid
from urllib2 import HTTPError

import ddt
import mock
from mock import Mock, patch


from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings


from accounts.controller import ProcessAccessKeyResult
from accounts.models import RemoteUser
from accounts.tests.utils import ApplyPatchMixin
from accounts.views import _cleanup_username as cleanup_username
from accounts.views import MISSING_ACCESS_KEY_ERROR, access_key
from admin.models import AccessKey, ClientCustomization
from api_client.api_error import ApiError


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


class SsoLoginTest(TestCase, ApplyPatchMixin):
    def setUp(self):
        super(SsoLoginTest, self).setUp()
        self.apply_patch('django_assets.templatetags.assets.AssetsNode.render', return_value='')

    def test_no_provider(self):
        """
        Users without SSO should end up back at the normal login form.
        """
        response = self.client.post(reverse('login'), {
            'sso_login_form_marker': '',
            'email': 'foo@bar.com',
        })
        self.assertTrue(response.context['error'])
        self.assertEqual(self.client.cookies['login_mode'].value, 'normal')


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

    def test_sso_flow(self):
        response = self.client.get('/access/{}'.format(self.access_key.code))
        self.assertEqual(response.status_code, 200)
        # That will then redirect us to the SSO provider...
        self.assertTrue(response.context['redirect_to'].startswith('/auth/login/tpa-saml/?'))
        for pair in ('auth_entry=apros', 'idp=testshib', 'next=%2Faccounts%2Flogin%2F'):
            self.assertIn(pair, response.context['redirect_to'])

        # The user then logs in and gets redirected back to Apros:
        response = self.client.post('/accounts/finalize/', data=self.SAMPLE_SSO_POST_DATA)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/accounts/sso_reg/')

        response = self.client.get(response['Location'])
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertEqual(form.is_bound, False)
        self.assertEqual(form.initial['username'], 'myself')
        self.assertEqual(form.initial['full_name'], 'Me Myself And I')
        self.assertEqual(form.initial['email'], 'myself@testshib.org')
        self.assertEqual(form.initial['company'], 'TestCo')

    @override_settings(SSO_AUTOPROVISION_PROVIDERS=['saml-testshib'])
    @patch('api_client.user_api.register_user')
    @patch('django.contrib.auth.login')
    @ddt.data(True, False)
    def test_sso_autoprovision_flow(self, with_existing_user, mock_login, mock_register_user):
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
        http_error = HTTPError("http://irrelevant", 409, error_reason, None, None)
        api_error = ApiError(http_error, "create_user", None)

        with mock.patch('accounts.views.user_api') as user_api_mock:
            user_api_mock.register_user.side_effect = self.make_raise_exception_side_effect(api_error)
            self.client.session['provider_data'] = {}

            response = self.client.post('/accounts/sso_reg/', data={
                'username': 'myself',
                'full_name': 'Me Myself And I',
                'email': 'myself@testshib.org',
                'city': 'Mogadishu',
                'accept_terms': True
            })

        self.assertIn('error', response.context)
        self.assertIn(error_reason, response.context['error'])
        self.assertIn('Failed to register user', response.context['error'])