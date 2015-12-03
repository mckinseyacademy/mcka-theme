from urllib2 import HTTPError
import ddt
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
import mock
from api_client.api_error import ApiError

from .forms import ActivationForm, FinalizeRegistrationForm
from .models import UserActivation, RemoteUser
from .views import access_key, MISSING_ACCESS_KEY_ERROR, _cleanup_username as cleanup_username
from admin.models import AccessKey, ClientCustomization
from mock import patch, Mock
import uuid


class AccountsFormsTests(TestCase):
    """
    Test Accounts Forms
    """
    def test_ActivationForm(self):
        # valid if data is good
        reg_data = {
            'username': 'testuser',
            'email': 'testuser@edx.org',
            'password': 'p455w0rd',
            'confirm_password': 'p455w0rd',
            'first_name': 'Test',
            'last_name': 'User',
            'city': 'Test City',
            'accept_terms': True,
        }
        activation_form = ActivationForm(reg_data)

        self.assertTrue(activation_form.is_valid())

    def test_FinalizeRegistrationForm(self):
        user_data = {
            'username': 'custom',
            'email': 'hacked@override.com',
            'full_name': 'Boberoo',
            'city': 'Testerville',
            'accept_terms': True,
        }
        fixed_data = {'email': 'bsmith@company.com', 'full_name': 'Bob Smith'}
        initial = {'username': 'bsmith'}

        form = FinalizeRegistrationForm(user_data, fixed_values=fixed_data, initial=initial)
        self.assertTrue(form.is_valid())
        # Users cannot override fixed_data:
        self.assertEqual(form.cleaned_data['email'], 'bsmith@company.com')
        self.assertEqual(form.cleaned_data['full_name'], 'Bob Smith')
        # But they can override 'initial' data
        self.assertEqual(form.cleaned_data['username'], 'custom')
        self.assertEqual(form.cleaned_data['city'], 'Testerville')


class TestUserObject(object):
    id = None
    email = None

    def __init__(self, user_id, email):
        self.id = user_id
        self.email = email


class UserActivationTests(TestCase):

    def test_activation(self):
        user = TestUserObject(100, "test_email@email.org")

        activation_record = UserActivation.user_activation(user)

        # If activation is broken this should raise UserActivation.DoesNotExist, hence no explicit assertions
        UserActivation.objects.get(activation_key=activation_record.activation_key)


class AccessLandingTests(TestCase):
    """
    Test view for handling invitation URLs
    """

    def apply_patch(self, *args, **kwargs):
        patcher = patch(*args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

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
        response = access_key(request, 1234)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.mock_client.add_user.called)

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
class TestUsernameCleanup(TestCase):
    """
    Test the _cleanup_username() method in views.py used during SSO logins.
    """
    def setUp(self):
        super(TestUsernameCleanup, self).setUp()
        get_users_patch = patch('api_client.user_api.get_users', self.mocked_get_users)
        get_users_patch.start()
        self.addCleanup(get_users_patch.stop)

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
class SsoUserFinalizationTests(TestCase):
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

    def apply_patch(self, *args, **kwargs):
        patcher = patch(*args, **kwargs)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock

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
        expected_username = 'myself' if not with_existing_user else 'myself1'
        mock_register_user.assert_called_once_with({
            'username': expected_username,
            'city': 'Gotham',
            'title': '',
            'country': '',
            'company': 'TestCo',
            'is_active': True,
            'year_of_birth': '',
            'level_of_education': '',
            'full_name': 'Me Myself And I',
            'gender': '',
            'accept_terms': True,
            'password': 'MDAwMA==',
            'email': 'myself@testshib.org',
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
