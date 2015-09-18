from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.test import TestCase

from .forms import ActivationForm, FinalizeRegistrationForm
from .models import UserActivation
from admin.models import AccessKey
from mock import patch, Mock
import uuid


class AccountsFormsTests(TestCase):

    ''' Test Accounts Forms '''

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


class TestUserObject():
    id = None
    email = None

    def __init__(self, id, email):
        self.id = id
        self.email = email

class UserActivationTests(TestCase):

    def test_activation(self):
        user = TestUserObject(100, "test_email@email.org")

        activation_record = UserActivation.user_activation(user)

        recalled_record = UserActivation.objects.get(activation_key=activation_record.activation_key)


class SsoUserFinalizationTests(TestCase):
    """
    Test 'finalizing' (registering) user's account when they sign up with SSO
    using an access key.
    """
    SAMPLE_REQUEST_URL = (
        '/accounts/finalize/?data=eyJ1c2VyX2RldGFpbHMiOiB7InVzZXJuYW1lIjogIm15c2VsZiIsICJmdWxsbm'
        'FtZSI6ICJNZSBNeXNlbGYgQW5kIEkiLCAibGFzdF9uYW1lIjogIkFuZCBJIiwgImZpcnN0X25hbWUiOiAiTWUg'
        'TXlzZWxmIiwgImVtYWlsIjogIm15c2VsZkB0ZXN0c2hpYi5vcmcifX0%3D'
        '&hmac=GHA2kEmdlxdgjmWbmAK4oa6bVxIJD3U755CyTO%2B1i%2FI%3D'
    )

    def apply_patch(self, *args, **kwargs):
        patcher = patch(*args, **kwargs)
        patcher.start()
        self.addCleanup(patcher.stop)

    def setUp(self):
        super(SsoUserFinalizationTests, self).setUp()
        # Since we're not logged in for these tests, we must manually create a test client session:
        self.client.cookies['sessionid'] = 'test_lms_session_id'
        self.client_id = 100
        self.access_key = AccessKey.objects.create(client_id=self.client_id, code=uuid.uuid4())
        session = {'sso_access_key_id': self.access_key.id}
        
        self.apply_patch('django.contrib.sessions.backends.base.SessionBase._session', session)
        self.apply_patch('api_client.organization_api.fetch_organization', return_value=Mock(display_name='TestCo'))

        def mock_render(_r, _t, data=None, status=200):
            self.response_data = data
            return HttpResponse('mocked template with data: {}'.format(data))

        self.apply_patch('django.shortcuts.render', mock_render)

    def test_form(self):
        response = self.client.get(self.SAMPLE_REQUEST_URL)
        self.assertEqual(response.status_code, 200)
        form = self.response_data['form']
        self.assertEqual(form.is_bound, False)
        self.assertEqual(form.initial['username'], 'myself')
        self.assertEqual(form.initial['full_name'], 'Me Myself And I')
        self.assertEqual(form.initial['email'], 'myself@testshib.org')
        self.assertEqual(form.initial['company'], 'TestCo')
