# -*- coding: utf-8 -*-

""" Tests for utility methods in data_sanitizing.py """

import unittest

from util.data_sanitizing import *


class TestSanitizingMethods(unittest.TestCase):
    """
    Test cases for data sanitizing methods
    """
    def test_remove_diacritics(self):
        """
        Tests removal of diacritics (non-spacing marks) from string
        """
        self.assertEqual(remove_diacritics('Héllô'), 'Hello')

    def test_remove_characters(self):
        """
        Tests removing characters from string
        """
        text = '!@Sample value++'
        clean_text = remove_characters(text, settings.CSV_CHARACTERS_BLACKLIST)

        has_blacklist_characters = any(char in clean_text for char in settings.CSV_CHARACTERS_BLACKLIST)

        self.assertFalse(has_blacklist_characters)

    def test_prepend_formula_value(self):
        """
        Tests that formula containing values are prepended with apostrophe
        """
        text1 = "=cmd|'/C calc'!A0"
        text2 = "sum(10+10)"

        self.assertTrue(
            prepend_formula_value(text1).startswith("'") and prepend_formula_value(text2).startswith("'")
        )

    def test_clean_xss_characters(self):
        """
        Tests that xss characters are escaped
        """
        text = '<script>'
        escaped_text = clean_xss_characters(text)

        self.assertEqual(escaped_text, '&lt;script&gt;')

    def test_sanitize_data_default_methods(self):
        """
        Tests default methods of sanitizing method
        default methods include both xss and formula cleaning
        """
        test_data = {
            'name': '< Test + 101',
            'location': 'Test File',
            'type': 'Unit test',
            'status': 'Active++'
        }

        # only `props_to_clean` properties get cleaned, other remain intact
        props_to_clean = ['name']

        cleaned_data = sanitize_data(test_data, props_to_clean)

        self.assertTrue(
            cleaned_data['name'].startswith("'") and '&lt;' in cleaned_data['name'] and
            cleaned_data['status'] == test_data['status']
        )

    def test_sanitize_data_selective_methods(self):
        """
        Tests that specified methods are applied on data
        """
        test_data = {
            'name': '<script>Test102</script>',
            'location': 'Test File',
            'type': 'Unit test',
            'status': 'Active++'
        }

        props_to_clean = ['name', 'status']
        clean_methods = (clean_formula_characters, )

        cleaned_data = sanitize_data(test_data, props_to_clean, clean_methods)

        self.assertTrue(
            cleaned_data['name'] == test_data['name'] and cleaned_data['status'].startswith("'")
        )
