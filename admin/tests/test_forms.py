import datetime

from django.forms import ValidationError
from django.test import TestCase

from admin.forms import (ClientForm, ProgramForm, CreateAccessKeyForm, ShareAccessKeyForm, MultiEmailField,
                         MobileBrandingForm)


class AdminFormsTests(TestCase):
    ''' Test Admin Forms '''

    def test_client_form(self):
        # valid if data is good
        client_data = {
            "display_name": "company",
            "contact_name": "contact_name",
            "contact_phone": "phone",
            "contact_email": "email@email.com",
        }
        client_form = ClientForm(client_data)

        self.assertTrue(client_form.is_valid())

    def test_program_form(self):
        # valid if data is good
        program_data = {
            "display_name": "public_name",
            "name": "private_name",
            "start_date": datetime.datetime(2014, 1, 1),
            "end_date": datetime.datetime(2014, 12, 12),
        }
        program_form = ProgramForm(program_data)

        self.assertTrue(program_form.is_valid())

    def test_create_access_key_form(self):
        # valid if data is good
        form_data = {
            "client_id": 1,
            "name": "Test Key",
            "program_id": "",
            "course_id": "",
        }
        form = CreateAccessKeyForm(form_data)
        self.assertTrue(form.is_valid())

    def test_share_access_key_form(self):
        # valid if data is good
        form_data = {
            "recipients": "student1@testorg.org, student2@testorg.org",
            "message": "",
        }
        form = ShareAccessKeyForm(form_data)
        self.assertTrue(form.is_valid())

    def test_mobile_branding_form_valid(self):
        ''' Test MobileBrandingForm with valid data '''

        form_data_valid = {
            'completed_course_tint' : '#111AAA',
            'header_background_color': '#2aABCCDF',
            'lesson_navigation_color': '#aaaAAA',
            'navigation_text_color': '#1234BC12',
            'navigation_icon_color': '#FFFFFF',
        }
        form = MobileBrandingForm(form_data_valid)
        self.assertTrue(form.is_valid())

    def test_mobile_branding_form_invalid(self):
        ''' Test MobileBrandingForm with invalid data '''

        form_data_invalid = {
            'completed_course_tint': '111AAA',
            'header_background_color': '#2aABCCDFa',
            'lesson_navigation_color': '#aaa',
            'navigation_text_color': '#1ETYUU',
            'navigation_icon_color': '#zzzzzzzz',
        }
        form = MobileBrandingForm(form_data_invalid)
        self.assertFalse(form.is_valid())


class MultiEmailFieldTest(TestCase):
    def test_validation(self):
        f = MultiEmailField()
        self.assertRaisesMessage(ValidationError, "'This field is required.'", f.clean, None)
        self.assertRaisesMessage(ValidationError, "'This field is required.'", f.clean, '')
        self.assertRaisesMessage(ValidationError, "'Enter a valid email address (not-an-email-adress).'",
                                 f.clean, 'test1@testorg.org,  not-an-email-adress, test2@testorg.org')

    def test_normalization(self):
        f = MultiEmailField()
        self.assertEqual(f.clean('test1@testorg.org, test2@testorg.org'),
                         ['test1@testorg.org', 'test2@testorg.org'])
        self.assertEqual(f.clean(' test1@testorg.org  ,  ,, test2@testorg.org,,'),
                         ['test1@testorg.org', 'test2@testorg.org'])

