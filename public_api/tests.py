"""
Test cases for public_api app
"""
import json
from django.test import TestCase
from django.test.client import Client
from django.core import mail

from django.core.urlresolvers import reverse

from api_client.user_models import UserResponse
from accounts.tests.utils import ApplyPatchMixin


class UserPasswordResetViewTest(TestCase, ApplyPatchMixin):
    """
    Test the user activation view.
    """
    def setUp(self):
        """
        Setup user activation view tests
        """
        super(UserPasswordResetViewTest, self).setUp()
        self.client = Client()
        self.user_json = {
            'id': 1212,
            'username': u'test_user',
            'city': u'Boston',
            'first_name': u'test',
            'last_name': u'user',
            'title': u'',
            'country': u'US',
            'email': u'test@fake.com',
            'year_of_birth': u'',
            'gender': u'M',
            'full_name': u'Test User',
            'company': u'',
        }

    def _apply_get_users_api_patch(self, user_json=None):
        """
        Helper method to patch get user api
        """
        user_api = self.apply_patch('public_api.views.user_api')
        if user_json:
            user_api.get_users.return_value = [UserResponse(
                json.dumps(user_json)
            )]
        else:
            []

    def test_reset_password_without_email(self):
        """
        Test reset password without email
        """
        self._apply_get_users_api_patch()
        response = self.client.post(reverse('api_reset_password'), {})
        self.assertEqual(response.status_code, 400)

    def test_reset_password_with_invalid_email(self):
        """
        Test reset password with invalid email
        """
        self._apply_get_users_api_patch()
        response = self.client.post(
            reverse('api_reset_password'),
            {'email': 'testemailcom'}
        )
        self.assertEqual(response.status_code, 400)

    def test_reset_password_with_valid_email(self):
        """
        Test reset password with valid email
        """
        self._apply_get_users_api_patch(self.user_json)
        response = self.client.post(
            reverse('api_reset_password'),
            {'email': 'test@fake.com'}
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(response.status_code, 200)

    def test_reset_password_with_valid_wrong_email(self):
        """
        Test reset password with valid wrong email
        """
        self._apply_get_users_api_patch()
        response = self.client.post(
            reverse('api_reset_password'),
            {'email': 'test@test.com'}
        )
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(response.status_code, 422)
