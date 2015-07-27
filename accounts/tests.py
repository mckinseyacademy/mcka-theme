from django.test import TestCase

from .forms import ActivationForm
from .models import UserActivation

# Create your tests here.


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
        }
        activation_form = ActivationForm(reg_data)

        self.assertTrue(activation_form.is_valid())

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

