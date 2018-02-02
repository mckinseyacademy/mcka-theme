from datetime import datetime, timedelta

from django.test import TestCase

from accounts.models import UserActivation, UserPasswordReset
from accounts.tests.utils import TestUserObject

# TODO: Add Unit tests for RemoteUser class from models


class UserActivationTests(TestCase):
    def setUp(self):
        self.user = TestUserObject(100, "test_email@email.org")

    def test_activation(self):
        activation_record = UserActivation.user_activation(self.user)
        activation_record_test = UserActivation.objects.get(activation_key=activation_record.activation_key)
        self.assertEquals(activation_record, activation_record_test)

    def test_get_activation(self):
        UserActivation.user_activation(self.user)
        user_activation = UserActivation.get_user_activation(self.user)
        self.assertIsInstance(user_activation, UserActivation)

    def test_get_activation_by_task_key(self):
        setattr(self.user, 'first_name', 'first_name')
        setattr(self.user, 'last_name', 'last_name')
        UserActivation.user_activation_by_task_key(self.user, 'sample_key', 1)
        activation_records = UserActivation.get_activations_by_task_key('sample_key')
        self.assertEqual(len(activation_records), 1)

    def user_activation_by_task_key(self):
        setattr(self.user, 'first_name', 'first_name')
        setattr(self.user, 'last_name', 'last_name')
        UserActivation.user_activation(self.user)
        user_activation = UserActivation.user_activation_by_task_key(self.user, 'test_key', 1)
        self.assertIsInstance(user_activation, UserActivation)


class UserPasswordResetTests(TestCase):
    def setUp(self):
        self.user = TestUserObject(100, "test_email@email.org")

    def test_create_validation_record(self):
        password_reset_record = UserPasswordReset.create_record(self.user)
        self.assertIsInstance(password_reset_record, UserPasswordReset)

    def test_get_user_validation_record(self):
        record = UserPasswordReset.create_record(self.user)
        validation_record = UserPasswordReset.get_user_validation_record(self.user)
        self.assertEquals(validation_record, record)
        self.user.id = 200
        validation_record = UserPasswordReset.get_user_validation_record(self.user)
        self.assertIsNone(validation_record)

    def test_check_user_validation_record(self):
        UserPasswordReset.create_record(self.user)
        validation_record = UserPasswordReset.get_user_validation_record(self.user)
        reset_record = UserPasswordReset.check_user_validation_record(
            self.user,
            validation_record.validation_key,
            None
        )
        self.assertIsInstance(reset_record, UserPasswordReset)

    def test_check_user_without_validation_record(self):

        reset_record = UserPasswordReset.check_user_validation_record(self.user, '123456', None)
        self.assertIsNone(reset_record)

        activation_record = UserPasswordReset.create_record(self.user)
        activation_record.time_requested -= timedelta(days=2)
        activation_record.save()
        reset_record = UserPasswordReset.check_user_validation_record(
            self.user,
            activation_record.validation_key,
            None
        )
        self.assertIsNone(reset_record)

