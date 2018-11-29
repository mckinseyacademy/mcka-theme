# -*- coding: utf-8 -*-
import ddt
from django.core.exceptions import ValidationError
from django.test import TestCase

from util.validators import RoleTitleValidator, normalize_foreign_characters


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
