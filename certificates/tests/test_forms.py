"""
Tests for certificates django forms
"""
import httpretty

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.tests.utils import ApplyPatchMixin
from util.unit_test_helpers.test_api_responses import course as test_course_data

from ..forms import CertificateTemplateAssetForm, CertificateTemplateForm


class CertificateTemplateAssetFormTest(TestCase):
    """
    Test the Certificate Template Asset Form
    """
    def setUp(self):
        """
        Setup Certificate Template Asset form test
        """
        super(CertificateTemplateAssetFormTest, self).setUp()
        self.post_data = {'description': 'dumy description'}
        self.stylesheet = SimpleUploadedFile(
            'style.css',
            'dummy content',
            content_type='text/css'
        )
        self.file_data = {'asset': self.stylesheet}

    def test_template_asset_form_valid(self):
        """
        Test certificate template asset form with valid data
        """
        form = CertificateTemplateAssetForm(self.post_data, self.file_data)
        self.assertTrue(form.is_valid())

    @httpretty.activate
    def test_template_asset_form_invalid(self):
        """
        Test certificate template asset form with invalid data
        """
        test_course_data.setup_course_list_response()
        form = CertificateTemplateAssetForm(self.post_data)
        self.assertFalse(form.is_valid())

    @httpretty.activate
    def test_template_asset_form_penetration(self):
        """
        Test certificate template asset form with  pen test invalid data
        """
        test_course_data.setup_course_list_response()
        self.post_data['name'] = 'dummy <p>'
        form = CertificateTemplateForm(self.post_data)
        self.assertFalse(form.is_valid())


class CertificateTemplateFormTest(TestCase, ApplyPatchMixin):
    """
    Test the Certificate Template Form
    """
    def setUp(self):
        """
        Setup Certificate Template form test
        """
        super(CertificateTemplateFormTest, self).setUp()
        self.courses = [
            ('abc/123/test', 'Abc Course'), ('xyz/334/dummy', 'Xyz Course')
        ]
        self.post_data = {
            'name': 'test',
            'description': 'dummy',
            'template': '<p>dummy template</p>',
            'course_id': self.courses[0][0]
        }

    def _apply_courses_choice_list_patch(self):
        """
        Helper method to patch get_courses_choice_list_patch method
        """
        get_courses_choice_list = self.apply_patch(
            'certificates.forms.get_courses_choice_list'
        )
        get_courses_choice_list.return_value = self.courses

    def test_template_form_valid(self):
        """
        Test certificate template form with valid data
        """
        self._apply_courses_choice_list_patch()
        form = CertificateTemplateForm(self.post_data)
        self.assertTrue(form.is_valid())

    def test_template_form_invalid(self):
        """
        Test certificate template form with invalid data
        """
        self._apply_courses_choice_list_patch()
        self.post_data['name'] = ''
        form = CertificateTemplateForm(self.post_data)
        self.assertFalse(form.is_valid())

    def test_template_form_penetration(self):
        """
        Test certificate template form with  pen test invalid data
        """
        self._apply_courses_choice_list_patch()
        self.post_data['name'] = 'dummy <p>'
        form = CertificateTemplateForm(self.post_data)
        self.assertFalse(form.is_valid())
