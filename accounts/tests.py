from django.test import TestCase

from accounts.forms import RegistrationForm

# Create your tests here.

class AccountsFormsTests(TestCase):

    def test_RegistrationForm(self):
        # valid if data is good
        reg_data = {
            'username' : 'testuser',
            'email' : 'testuser@edx.org',
            'password' : 'p455w0rd',
            'confirm_password' : 'p455w0rd',
            'first_name' : 'Test',
            'last_name' : 'User',
        }
        registration_form = RegistrationForm(reg_data)

        self.assertTrue(registration_form.is_valid())

        # invalid if password fields do not match, but otherwise good
        reg_data['confirm_password'] = 'p455w0rd_not_matched'

        registration_form = RegistrationForm(reg_data)

        self.assertFalse(registration_form.is_valid())
