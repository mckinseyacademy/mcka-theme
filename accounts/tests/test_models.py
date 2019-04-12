# -*- coding: utf-8 -*-
import ddt

from datetime import timedelta
from mock import MagicMock

from django.test import TestCase

from accounts.models import UserActivation, UserPasswordReset, RemoteUser
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
        UserActivation.user_activation_by_task_key(
            self.user.id, self.user.email, self.user.first_name, self.user.last_name,
            'sample_key', 1
        )
        activation_records = UserActivation.get_activations_by_task_key('sample_key')
        self.assertEqual(len(activation_records), 1)

    def user_activation_by_task_key(self):
        setattr(self.user, 'first_name', 'first_name')
        setattr(self.user, 'last_name', 'last_name')
        UserActivation.user_activation(self.user)
        user_activation = UserActivation.user_activation_by_task_key(
            self.user.id, self.user.email, self.user.first_name, self.user.last_name,
            'test_key', 1
        )
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


@ddt.ddt
class RemoteUserTest(TestCase):

    @ddt.data(
        ('John', 'Doe', 'john.doe@corp.com', 11),
        (u'فلانة', u'الفلاني', 'abc@xyz.ar', 22),
        (u'कोई', u'व्यक्ति', 'xyz@abc.in', 33),
    )
    @ddt.unpack
    def test_update_response_fields(self, first_name, last_name, email, user_id):
        user_response_mock = MagicMock()
        user_response_mock.first_name = first_name
        user_response_mock.last_name = last_name
        user_response_mock.email = email
        user_response_mock.id = user_id
        user = RemoteUser()
        user.update_response_fields(user_response_mock)
        self.assertTrue(user.first_name in user.fullname)
        self.assertTrue(user.last_name in user.fullname)
        self.assertEqual(user.name_initials[0], first_name[0])
        self.assertEqual(user.name_initials[1], last_name[0])
