# -*- coding: utf-8 -*-
import ddt
from django.core.exceptions import ValidationError
from django.test import TestCase


from util.validators import RoleTitleValidator, normalize_foreign_characters, UsernameValidator,\
    AlphanumericValidator, \
    PhoneNumberValidator, validate_first_name


@ddt.ddt
class TestRoleTitleValidator(TestCase):
    """ Test custom RoleTitleValidator from utils/validators.py"""
    def setUp(self):
        self.validator = RoleTitleValidator()

    @ddt.data(
        'Senior Executive (e.g., CXO, SVP)',
        'Seasoned Leader/Senior Manager (e.g., VP, Director)',
        'Mid-Level Manager (e.g., Manager)',
        'Early Career Professional (e.g., Associate, Analyst)',
        'Other (please describe below)'
    )
    def test_with_valid_input(self, test_text):
        """ With valid input which passes the regex"""
        self.assertIsNone(self.validator(test_text))

    @ddt.data(
        '@#$@%@$#23',
        'Seasoned {Leader/Senior Manager} (e.g., VP, Director)',
        '%Seasoned Leader/Senior Manager (e.g., VP, Director)',
    )
    def test_with_invalid_input(self, test_text):
        """With in_valid input which doesnt passes the regex"""
        with self.assertRaises(ValidationError):
            self.validator(test_text)


class TestNormalizeCsvForeignCharacters(TestCase):
    """Test the method normalize_foreign_characters from utils/validators.py"""

    def test_normalize_foreign_characters(self):
        normalize_grave_characters = normalize_foreign_characters("testàèìòùÀÈÌÒÙ")
        self.assertEqual(normalize_grave_characters, 'testaeiouAEIOU')

        normalize_acute_characters = normalize_foreign_characters("testáéíóúýÁÉÍÓÚÝ")
        self.assertEqual(normalize_acute_characters, 'testaeiouyAEIOUY')

        normalize_caret_characters = normalize_foreign_characters("testâêîôûðÂÊÎÔÛÐ")
        self.assertEqual(normalize_caret_characters, 'testaeiouAEIOU')

        normalize_tilde_characters = normalize_foreign_characters("testãñõÃÑÕ")
        self.assertEqual(normalize_tilde_characters, 'testanoANO')

        normalize_umlaut_characters = normalize_foreign_characters("testäëïöüÿÄËÏÖÜŸ")
        self.assertEqual(normalize_umlaut_characters, 'testaeiouyAEIOUY')

        normalize_other_foreign_characters = normalize_foreign_characters("teståÅðÇ")
        self.assertEqual(normalize_other_foreign_characters, 'testaAC')


@ddt.ddt
class TestUsernameValidator(TestCase):
    """"For testing username UsernameValidator"""
    def setUp(self):
        self.validator = UsernameValidator()

    @ddt.data(
        'Manager',
        'Company-manager',
        'group_member'
    )
    def test_with_valid_username(self, username):
        """Testing with valid inputs"""
        self.assertIsNone(self.validator(username))

    @ddt.data(
        '@#$@%@$#23',
        '{}/',
        '%member',
        ' m.member -',
        '(Group Lead)'
    )
    def test_with_invalid_username(self, username):
        """Testing with invalid inputs"""
        with self.assertRaises(ValidationError):
            self.validator(username)


@ddt.ddt
class TestAlphanumericValidator(TestCase):
    """Testing AlphanumericValidator"""
    def setUp(self):
        self.validator = AlphanumericValidator()

    @ddt.data(
        'Manager',
        'Company-manager',
        'Company manager',
        'group_member'
    )
    def test_with_valid_expression(self, string_to_validate):
        """Testing with valid inputs"""
        self.assertIsNone(self.validator(string_to_validate))

    @ddt.data(
        '@#$@%@$#23',
        '{}/',
        '%memeber',
        '$ m.member -',
        '(Group Admin)'
    )
    def test_with_invalid_expression(self, string_to_validate):
        """Testing with invalid inputs"""
        with self.assertRaises(ValidationError):
            self.validator(string_to_validate)


@ddt.ddt
class TestPhoneNumberValidator(TestCase):
    """Test cases for PhoneNumberValidator"""
    def setUp(self):
        self.validator = PhoneNumberValidator()

    @ddt.data(
        '(+351) 282 43 50 50',
        '90191919908',
        '555-8909',
        '001 6867684',
        '001 6867684x1',
        '1 (234) 567-8901',
        '1-234-567-8901 x1234',
        '1-234-567-8901 ext1234',
        '1-234 567.89/01 ext.1234',
        '1(234)5678901x1234',
        '(123)8575973',
        '(0055)(123)8575973'
    )
    def test_with_valid_phone_number(self, phone_number):
        """With valid inputs"""
        self.assertIsNone(self.validator(phone_number))

    @ddt.data(
        '(+351) 282 43 W50 50',
        '90191919908#',
        '555-8909{',
        '_001 6867684',
        '001 +6867684x1',
        '1 (234) =567-8901',
        '`1-234-567-8901 x1234',
        '(0055)}orphk]'
    )
    def test_with_invalid_phone_number(self, phone_number):
        """With invalid inputs"""
        with self.assertRaises(ValidationError):
            self.validator(phone_number)


@ddt.ddt
class ValidateFirstName(TestCase):
    """Testing validate_first_name"""
    @ddt.data(
        'manager',
        'Organization-Manager á',
        'Supervisor ñ',
        'company_Advisor ç'
    )
    def test_valid_name(self, name):
        """With valid inputs"""
        self.assertIsNone(validate_first_name(name))

    @ddt.data(
        '@#$@%@$#23',
        '{}/',
        '%Advisor',
        '$ m.usman -',
        '(Company Advisor)'
    )
    def test_invalid_name(self, name):
        """With invalid inputs"""
        with self.assertRaises(ValidationError):
            validate_first_name(name)


@ddt.ddt
class ValidateLasttName(TestCase):
    """Testing validate_first_name"""
    @ddt.data(
        'galâ',
        'Company-Manager á',
        'lead_member ç'
    )
    def test_valid_name(self, name):
        """With valid inputs"""
        self.assertIsNone(validate_first_name(name))

    @ddt.data(
        '@#$@%@$#23',
        '{}/',
        '%member',
        '$ m.member -',
        '(Group Lead)'
    )
    def test_invalid_name(self, name):
        """With invalid inputs"""
        with self.assertRaises(ValidationError):
            validate_first_name(name)
