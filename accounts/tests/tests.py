from urllib2 import HTTPError
import ddt
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
import mock

from accounts.controller import ProcessAccessKeyResult, process_access_key, AssignStudentToProgramResult, \
    EnrollStudentInCourseResult, enroll_student_in_course, has_mobile_ready_course
from accounts.json_backend import JsonBackend
from api_client.api_error import ApiError
from api_client.course_models import CourseListCourse
from api_client.organization_models import Organization
from api_client.user_models import AuthenticationResponse, UserResponse
from accounts.forms import ActivationForm, FinalizeRegistrationForm
from accounts.models import UserActivation, RemoteUser
from accounts.views import access_key, MISSING_ACCESS_KEY_ERROR, _cleanup_username as cleanup_username, login
from admin.models import AccessKey, ClientCustomization, Program
from mock import patch, Mock
import uuid


class ApplyPatchMixin(object):
    """ Mixin with patch helper method """
    def apply_patch(self, *args, **kwargs):
        """
        Applies patch and registers a callback to stop the patch in TearDown method
        """
        patcher = patch(*args, **kwargs)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock


def _make_user(username='johndoe', email='john@doe.org', password='password'):
    return RemoteUser.objects.create_user(username=username, email=email, password=password)


def _make_company(org_id, display_name='company_name'):
    return Organization(dictionary={'id': org_id, 'display_name': display_name})


def _make_program(prog_id=1, display_name='Test program', courses=None):
    courses = courses if courses else []
    program = Program(dictionary={'id': prog_id, 'display_name': display_name})
    program.courses = courses
    return program


def _make_course(course_id='course_id', display_name='Course Name'):
    return CourseListCourse(dictionary={'course_id': course_id, 'display_name': display_name})


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
        existing_user = _make_user()
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
        existing_user = _make_user(username='username', password='password')
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
        existing_user = _make_user()

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
        existing_user = _make_user()

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
        existing_user = _make_user()

        self.user_api.authenticate.return_value = self._make_auth_response(existing_user)
        self.user_api.get_session.return_value = mock.Mock(user_id=existing_user.id)
        self.user_api.get_user.return_value = self._make_user_response(existing_user)

        self.backend.authenticate(remote_session_key=None)
        self.user_api.authenticate.assert_called_once_with(None, None, remote_session_key=None)
        self.user_api.get_session.assert_not_called()


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


class TestProcessAccessKey(TestCase, ApplyPatchMixin):
    """ Tests process_access_key method """
    program = None

    @classmethod
    def setUpClass(cls):
        super(TestProcessAccessKey, cls).setUpClass()
        cls.program = _make_program()

    def setUp(self):
        self.user_api = self.apply_patch('accounts.controller.user_api')
        self.apply_patch(
            'accounts.controller.assign_student_to_program',
            return_value=AssignStudentToProgramResult(self.program, None)
        )
        self.patched_enroll_student_in_course = self.apply_patch('accounts.controller.enroll_student_in_course')
        self.user_api.get_user_organizations = mock.Mock(return_value=[_make_company(1)])

    def test_not_registered_with_company(self):
        user = _make_user()
        key = AccessKey.objects.create(client_id=1, code=1234)
        company = _make_company(1, display_name='Other company')
        self.user_api.get_user_organizations = mock.Mock(return_value=[_make_company(1000)])

        result = process_access_key(user, key, company)
        self.assertIsNone(result.enrolled_in_course_ids)
        self.assertIsNone(result.new_enrollements_course_ids)
        self.assertEqual(len(result.messages), 1)
        message = result.messages[0]
        expected_message = "Access Key {key} is associated with company {company}, " \
                           "but you're not registered with it".format(key=key.code, company=company.display_name)
        self.assertEqual(message[1], expected_message)

    def test_adds_new_enrollment_to_enrolled_courses(self):
        course_id = "Course QWERTY"
        user = _make_user()
        key = AccessKey.objects.create(client_id=1, code=1234, program_id=self.program.id, course_id=course_id)
        company = _make_company(1, display_name='Other company')
        self.patched_enroll_student_in_course.return_value = EnrollStudentInCourseResult(course_id, True, True, None)

        result = process_access_key(user, key, company)
        self.assertEqual(result.enrolled_in_course_ids, [course_id])
        self.assertEqual(result.new_enrollements_course_ids, [course_id])

    def test_adds_existing_enrollment_to_enrolled_courses(self):
        course_id = "Course QWERTY"
        user = _make_user()
        key = AccessKey.objects.create(client_id=1, code=1234, program_id=self.program.id, course_id=course_id)
        company = _make_company(1, display_name='Other company')
        self.patched_enroll_student_in_course.return_value = EnrollStudentInCourseResult(course_id, True, False, None)

        result = process_access_key(user, key, company)
        self.assertEqual(result.enrolled_in_course_ids, [course_id])
        self.assertEqual(result.new_enrollements_course_ids, [])

    def test_skips_course_if_not_enrolled(self):
        course_id = "Course QWERTY"
        user = _make_user()
        key = AccessKey.objects.create(client_id=1, code=1234, program_id=self.program.id, course_id=course_id)
        company = _make_company(1, display_name='Other company')
        self.patched_enroll_student_in_course.return_value = EnrollStudentInCourseResult(
            course_id, False, False, "Message"
        )

        result = process_access_key(user, key, company)
        self.assertEqual(result.enrolled_in_course_ids, [])
        self.assertEqual(result.new_enrollements_course_ids, [])
        self.assertEqual(result.messages, ["Message"])


class TestEnrollStudentInCourse(TestCase, ApplyPatchMixin):
    """ Tests for enroll_student_in_course method """
    def _assert_result(self, result, course_id, expected_message, enrolled, new_enrollement):
        self.assertEqual(result.course_id, course_id)
        self.assertEqual(result.message, expected_message)
        self.assertEqual(result.enrolled, enrolled)
        self.assertEqual(result.new_enrollment, new_enrollement)

    def _make_side_effect_raise_api_error(self, api_error_code):
        thrown_error = mock.Mock()
        thrown_error.code = api_error_code
        thrown_error.reason = "I have no idea, but luckily it is irrelevant for the test"

        def _raise(*args, **kwargs):
            raise ApiError(thrown_error=thrown_error, function_name='irrelevant')
        return _raise

    def setUp(self):
        self.user_api = self.apply_patch('accounts.controller.user_api')

    def test_invalid_course_id(self):
        user = _make_user()
        program = _make_program(courses=[_make_course(course_id_iter) for course_id_iter in [1, 2]])
        course_id = 'qwerty'

        result = enroll_student_in_course(user, program, course_id)
        expected_message = 'Unable to enroll you in course "{}" - it is no longer part of your program.'.format(
            course_id
        )
        self._assert_result(result, course_id, (messages.ERROR, expected_message), False, False)

    def test_new_enrollment(self):
        course_id = 'qwerty'
        user = _make_user()
        program = _make_program(courses=[_make_course(course_id)])

        result = enroll_student_in_course(user, program, course_id)
        expected_message = "Successfully enrolled you in a course {}.".format(course_id)
        self._assert_result(result, course_id, (messages.INFO, expected_message), True, True)

    def test_already_enrolled(self):
        course_id = 'qwerty'
        user = _make_user()
        program = _make_program(courses=[_make_course(course_id)])
        self.user_api.enroll_user_in_course.side_effect = self._make_side_effect_raise_api_error(409)

        result = enroll_student_in_course(user, program, course_id)
        expected_message = 'You are already enrolled in course "{}"'.format(course_id)
        self._assert_result(result, course_id, (messages.INFO, expected_message), True, False)

    def test_failed_to_eroll(self):
        course_id = 'qwerty'
        user = _make_user()
        program = _make_program(courses=[_make_course(course_id)])
        self.user_api.enroll_user_in_course.side_effect = self._make_side_effect_raise_api_error(400)

        result = enroll_student_in_course(user, program, course_id)
        expected_message = 'Unable to enroll you in course "{}".'.format(course_id)
        self._assert_result(result, course_id, (messages.ERROR, expected_message), False, False)


class AccountControllerTest(TestCase, ApplyPatchMixin):
    """
    Test cases for accounts related helper methods
    """
    def setUp(self):
        """
        Sets up the test case
        """
        super(AccountControllerTest, self).setUp()
        self.user_courses_progress_response = [
            {
                "created": "2017-09-13T10:10:52.804706Z",
                "is_active": "true",
                "progress": 0,
                "course": {
                    "end": "null",
                    "mobile_available": "true",
                    "start": "2017-08-01T01:00:00Z",
                    "display_name": "Certificate Demo for OPS",
                    "id": "edx/CS111/2017",
                    "course_image_url": "/c4x/edx/CS111/asset/McKA_course_tile_BusStrat.png"
                }
            }
        ]

        self.get_user_courses_progress = self.apply_patch(
            'accounts.controller.get_user_courses_progress'
        )

    def test_has_mobile_ready_course_with_mobile_ready_courses(self):
        """
        Tests has_mobile_ready_course helper method when user has mobile ready courses
        """
        user_id = 4
        self.get_user_courses_progress.return_value = self.user_courses_progress_response
        self.assertTrue(has_mobile_ready_course(user_id))

    def test_has_mobile_ready_course_without_mobile_ready_courses(self):
        """
        Tests has_mobile_ready_course helper method when user has no mobile ready courses
        """
        user_id = 4
        self.get_user_courses_progress.return_value = []
        self.assertFalse(has_mobile_ready_course(user_id))
