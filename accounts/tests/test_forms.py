from django.test import TestCase

from accounts.forms import ActivationForm, FinalizeRegistrationForm


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
