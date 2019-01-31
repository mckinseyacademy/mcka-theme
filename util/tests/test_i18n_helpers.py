# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import translation

from accounts.tests.utils import ApplyPatchMixin
from ..i18n_helpers import set_language


class I18nHelperTest(TestCase, ApplyPatchMixin):
    """
    Test the course controller.
    """
    def setUp(self):
        """
        Setup course controller tests
        """
        super(I18nHelperTest, self).setUp()
        self.request = RequestFactory()
        self.request.LANGUAGE_CODE = 'en-us'
        self.request.session = {}

    def test_set_language(self):
        """
        Test language setter function
        """
        get_current_request = self.apply_patch('util.i18n_helpers.get_current_request')
        get_current_request.return_value = self.request

        language = 'ar'
        set_language(language)
        self.assertEqual(language, translation.get_language())
        self.assertEqual(language, self.request.session[translation.LANGUAGE_SESSION_KEY])

    def tearDown(self):
        set_language('en-us')
