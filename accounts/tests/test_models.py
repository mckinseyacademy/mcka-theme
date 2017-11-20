from django.test import TestCase

from accounts.models import UserActivation
from accounts.tests.utils import TestUserObject


class UserActivationTests(TestCase):
    def test_activation(self):
        user = TestUserObject(100, "test_email@email.org")

        activation_record = UserActivation.user_activation(user)

        # If activation is broken this should raise UserActivation.DoesNotExist, hence no explicit assertions
        UserActivation.objects.get(activation_key=activation_record.activation_key)
