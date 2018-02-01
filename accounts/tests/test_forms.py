from django.test import TestCase
from django.core import mail
import ddt

from admin.models import SelfRegistrationRoles, CourseRun, OTHER_ROLE
from lib.utils import DottableDict
from accounts.forms import ActivationForm, FinalizeRegistrationForm, BaseRegistrationForm,\
    FpasswordForm, SetNewPasswordForm, BaseRegistrationFormV2, PublicRegistrationForm, SSOLoginForm,\
    LoginForm, EditFullNameForm, EditTitleForm, ActivationFormV2

from accounts.tests.utils import ApplyPatchMixin


@ddt.ddt
class SSOLoginFormTests(TestCase):
    """ Tests for SSOLoginForm """

    @ddt.data(
        ({"sso_login_form_marker": "test", "email": "test@gmail.com"}, True),
        ({"sso_login_form_marker": "12345", "email": "test_test44@mackinsey.com"}, True),
        ({"sso_login_form_marker": "test", "email": "test.com"}, False),
    )
    @ddt.unpack
    def test_validation(self, test_case, expected_result):
        """ Test validation """
        login_form = SSOLoginForm(test_case)
        self.assertEqual(login_form.is_valid(), expected_result)


@ddt.ddt
class LoginFormTests(TestCase):
    """ Tests for LoginForm """

    @ddt.data(
        ({"username": "test", "password": "tewerrr45st@gmail.com"}, True),
        ({"username": "test123", "password": "test"}, True),
        ({"username": "test", "password": None}, False),
        ({"username": None, "password": "test"}, False),

    )
    @ddt.unpack
    def test_validation(self, test_case, expected_result):
        """ Test validation """
        login_form = LoginForm(test_case)
        self.assertEqual(login_form.is_valid(), expected_result)


@ddt.ddt
class EditFullNameFormTests(TestCase):
    """ Tests for EditFullNameForm """

    @ddt.data(
        ({"first_name": "test", "last_name": "user"}, True),
        ({"first_name": "test123", "last_name": None}, False),
        ({"first_name": "1234", "last_name": "5678"}, True),

    )
    @ddt.unpack
    def test_validation(self, test_case, expected_result):
        """ Test validation """
        edit_name_form = EditFullNameForm(test_case)
        self.assertEqual(edit_name_form.is_valid(), expected_result)


@ddt.ddt
class EditTitleFormTests(TestCase):
    """ Tests for EditTitleForm """

    @ddt.data(
        ({"title": "test"}, True),
        ({"title": "test4566"}, True),
        ({"title": 1234}, True),
        ({}, True),

    )
    @ddt.unpack
    def test_validation(self, test_case, expected_result):
        """ Test validation """
        edit_title_form = EditTitleForm(test_case)
        self.assertEqual(edit_title_form.is_valid(), expected_result)


@ddt.ddt
class BaseRegistrationFormTests(TestCase):
    """ Tests for BaseRegistrationForm """

    @ddt.data(
        (False, False),
        (True, True),
        ('', False),
        (None, False)
    )
    @ddt.unpack
    def test_clean_accept_terms(self, accept_terms, expected_result):
        """ Test for clean accept terms"""

        registration_data = {
            'username': 'testuser',
            'email': 'testuser@edx.org',
            'password': 'p455w0rd',
            'city': 'lahore',
            'accept_terms': accept_terms
        }
        registration_form = BaseRegistrationForm(registration_data)
        self.assertEqual(registration_form.is_valid(), expected_result)


@ddt.ddt
class FpasswordFormTests(TestCase, ApplyPatchMixin):
    """ Tests for FpasswordFormTests """

    empty_users = []
    active_users = [
        DottableDict(id=1, email='active@gmail.com', is_active=True),
    ]
    inactive_users = [
        DottableDict(id=2, email='notactive@gmail.com', is_active=False),
    ]

    def _apply_get_users_patch(self, users):
        """ Helper method to patch get_users function """

        get_users = self.apply_patch('api_client.user_api.get_users')
        get_users.return_value = users

    @ddt.data(
        ('active@gmail.com', True, active_users),
        ('notactive@gmail.com', False, inactive_users)
    )
    @ddt.unpack
    def test_clean_email(self, email, expected_result, users):
        """ Test for clean_email """

        email_data = {
            'email': email,
        }
        self._apply_get_users_patch(users)
        pass_reset_form = FpasswordForm(email_data)
        self.assertEqual(pass_reset_form.is_valid(), expected_result)

    @ddt.data(
        ('notactive@gmail.com', False, inactive_users),
        ('empty@gmail.com', False, empty_users),
        ('active@gmail.com', True, active_users),
    )
    @ddt.unpack
    def test_save(self, email, expected_result, users):
        """ Test for save method """
        email_data = {
            'email': email,
        }
        self._apply_get_users_patch(users)
        pass_reset_form = FpasswordForm(email_data)
        if pass_reset_form.is_valid():
            request = DottableDict(META={})
            pass_reset_form.save(request=request)
            result = email in [email.to[0] for email in mail.outbox]
            self.assertEqual(result, expected_result)
        else:
            self.assertFalse(expected_result)


@ddt.ddt
class SetNewPasswordFormTests(TestCase, ApplyPatchMixin):
    """ Tests for SetNewPasswordFormTest """

    def _apply_update_user_information_patch(self, raise_exception):
        """ Helper method to patch update_user_information function """

        if not raise_exception:
            user = self.apply_patch('api_client.user_api.update_user_information')
            user.return_value = "success"

    @ddt.data(
        ('abcderf', 'abcderf', True),
        ('ABCDERF', 'abcderf', False),
        ('abcderf', 'abcderfedfgd', False),
        ('abcderfxcgfds', 'abcderf', False),
        ('', 'abcderf', False),
        ('abcderf', '', False),
    )
    @ddt.unpack
    def test_clean_new_password2(self, pass1, pass2, expected_result):
        """ Test for clean_new_password2 """

        user = DottableDict(id=1, email='active@gmail.com', is_active=True)
        passwords = {
            'new_password1': pass1,
            'new_password2': pass2
        }

        pass_form = SetNewPasswordForm(user, passwords)
        self.assertEqual(pass_form.is_valid(), expected_result)

    @ddt.data(
        ('abcderf', 'abcderf', True),
        ('abcderf', 'abcderf', True),
        ('ABCDERF', 'abcderf', False),
        ('abcderf', 'abcderfedfgd', False),
        ('abcderfxcgfds', 'abcderf', False),
        ('', 'abcderf', False),
        ('abcderf', '', False),
    )
    @ddt.unpack
    def test_save(self, pass1, pass2, raise_exception):
        """Test for save method """

        user = DottableDict(id=1, email='active@gmail.com', is_active=True)
        passwords = {
            'new_password1': pass1,
            'new_password2': pass2
        }
        self._apply_update_user_information_patch(raise_exception)
        pass_form = SetNewPasswordForm(user, passwords)
        if pass_form.is_valid():
            result = pass_form.save()
            self.assertEqual(bool(result.error), raise_exception)


@ddt.ddt
class BaseRegistrationFormV2Tests(TestCase):
    """ Tests for BaseRegistrationFormV2 """

    @ddt.data(
        (False, False),
        (True, True),
        ('', False),
        (None, False)
    )
    @ddt.unpack
    def test_clean_accept_terms(self, accept_terms, expected_result):
        """ Test for clean_accept_terms """

        registration_data = {
            'username': 'testuser',
            'email': 'testuser@edx.org',
            'password': 'p455w0rd',
            'city': 'lahore',
            'accept_terms': accept_terms
        }
        registration_form = BaseRegistrationFormV2(registration_data)
        self.assertEqual(registration_form.is_valid(), expected_result)


@ddt.ddt
class ActivationFormV2Tests(TestCase):
    """ Tests for ActivationFormV2 """

    @ddt.data(
        (None, False),
        ('', False),
        ("testuser", True),
        ("test123", True)
    )
    @ddt.unpack
    def test_form_validation(self, username, expected_result):
        """ Test form validation """

        registration_data = {
            'username': username,
            'email': 'testuser@edx.org',
            'password': 'p455w0rd',
            'city': 'lahore',
            'accept_terms': True
        }
        registration_form = ActivationFormV2(registration_data)
        self.assertEqual(registration_form.is_valid(), expected_result)

@ddt.ddt
class PublicRegistrationFormTests(TestCase):
    """ Tests for PublicRegistrationForm """

    def setUp(self):
        self.course_run = CourseRun.objects.create(
            name="abc", course_id="abc", email_template_new="email", email_template_existing="email",
            email_template_mcka="email", email_template_closed="email", self_registration_page_heading="abc",
            self_registration_description_text="abc")
        self.self_reg_role = SelfRegistrationRoles.objects.create(option_text="any", course_run=self.course_run)

    base_test_case = {
        'first_name': 'test',
        'last_name': 'test',
        'company_name': 'test',
        'company_email': 'company_email@mcka.com',
        'current_role': '1',
        'current_role_other': "Other Role"
    }
    char_field_test_set = [
        ('', False),
        (None, False),
        ('first name with only valid chars', True),
        ('first name with number 125', False),
        ('first name with special chars -', False),
        ('first name with special chars -34^4', False),
        ('first name with special chars :dl)"', False),
        ('first name wi7864th special chars', False),
        ('124first name with special chars', False),
        ('first name with special chars &', False),
        ('&*9)first name with special chars )(8*%', False),
    ]

    @ddt.data(
        *char_field_test_set
    )
    @ddt.unpack
    def test_clean_first_name(self, first_name, expected_result):
        """ Test for clean_first_name """

        test_case = self.base_test_case.copy()
        test_case['first_name'] = first_name
        test_case['current_role'] = str(self.self_reg_role.id)
        public_form = PublicRegistrationForm(test_case, course_run_name=self.course_run.name)
        self.assertEqual(public_form.is_valid(), expected_result)

    @ddt.data(
        *char_field_test_set
    )
    @ddt.unpack
    def test_clean_last_name(self, last_name, expected_result):
        """ Test for clean_last_name """

        test_case = self.base_test_case.copy()
        test_case['last_name'] = last_name
        test_case['current_role'] = str(self.self_reg_role.id)
        public_form = PublicRegistrationForm(test_case, course_run_name=self.course_run.name)
        self.assertEqual(public_form.is_valid(), expected_result)

    @ddt.data(
        ('', False),
        ('g@', False),
        (123445, False),
        (None, False),
        ('gmewrefwjs', False),
        ('valid_mail@mcka.com', True),
        ('not_valid@gmail.com', False),
        ('seventy_characters'*12 + 'a@mcka.com', False),
        ('more_than_seventy_characters'*9, False),
    )
    @ddt.unpack
    def test_clean_company_email(self, company_email, expected_result):
        """ Test for clean company_email """

        test_case = self.base_test_case.copy()
        test_case['company_email'] = company_email
        test_case['current_role'] = str(self.self_reg_role.id)
        public_form = PublicRegistrationForm(test_case, course_run_name=self.course_run.name)
        self.assertEqual(public_form.is_valid(), expected_result)

    @ddt.data(
        ('', False),
        (None, False),
        ('first name with number 125', True),
        ('first name with only valid chars', True),
        ('first name wi7864th special chars', True),
        ('2234first name wi7864th special chars', True),
        ('first name wi7864th special chars45', True),

        ('first name with special chars -', False),
        ('first name with special chars &', False),
        ('first name with special chars -34^4', False),
        ('first name with special chars :dl)"', False),
        ('&*9)first name with special chars )(8*%', False),
    )
    @ddt.unpack
    def test_clean_company_name(self, company_name, expected_result):
        """ Test for clean_company_name """

        test_case = self.base_test_case.copy()
        test_case['company_name'] = company_name
        test_case['current_role'] = str(self.self_reg_role.id)
        public_form = PublicRegistrationForm(test_case, course_run_name=self.course_run.name)
        self.assertEqual(public_form.is_valid(), expected_result)

    @ddt.data(
        ('', False),
        ('test', True),
        ('test123 876', True),
        ('123876', True),
        ('123876 $%%^', False),

    )
    @ddt.unpack
    def test_clean_current_role_other(self, current_other_role, expected_result):
        """ Test for clean_current_role_other """

        self_reg_role = SelfRegistrationRoles.objects.get(option_text=OTHER_ROLE, course_run=self.course_run)

        test_case = self.base_test_case.copy()
        test_case['current_role'] = str(self_reg_role.id)
        test_case['current_role_other'] = current_other_role
        public_form = PublicRegistrationForm(test_case, course_run_name=self.course_run.name)
        self.assertEqual(public_form.is_valid(), expected_result)


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
        activation_form = ActivationForm(reg_data, initial={'country': 'af'})

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
