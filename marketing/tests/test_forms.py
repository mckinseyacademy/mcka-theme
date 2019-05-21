from django.test import TestCase
from marketing.forms import TechSupportForm, SubscribeForm, EdxOfferForm
from mock import mock


class TechSupportFormsTests(TestCase):
    """
    Tests for TechSupportFormsTests
    """

    def setUp(self):
        """
        Sets up the initial form data
        """
        self.tech_support_data = {
            "type": "problem",
            "name": "name",
            "comment": "Some detail",
            "email": "email@email.com",
        }

    def test_tech_suppport_form_valid_data(self):
        """
        Verify that form is submitted with valid data
        """
        tech_support_form = TechSupportForm(self.tech_support_data)
        self.assertTrue(tech_support_form.is_valid())

    def test_tech_suppport_form_invalid_data(self):
        """
       Verify that form is not submitted with invalid data
       :return: errors
       """

        tech_support_data = {
            "type": "problem",
            "name": "name",
            "comment": "Some detail",
        }
        expected_errors = {'email': [u'This field is required.']}
        tech_support_form = TechSupportForm(tech_support_data)

        self.assertFalse(tech_support_form.is_valid())
        self.assertEqual(tech_support_form.errors, expected_errors)


def test_save_tech_support_form(self):
    """
    Asserts that form saves the data with valid data
    """
    with mock.patch('marketing.forms.TechSupportForm.save', return_value=self.tech_support_data):
        tech_support_form = TechSupportForm(self.tech_support_data)
        self.assertTrue(tech_support_form.is_valid())
        tech_support_data = tech_support_form.save()
        self.assertEqual(tech_support_data['name'], "name")
        self.assertEqual(tech_support_data['type'], "problem")
        self.assertEqual(tech_support_data['comment'], "Some detail")
        self.assertEqual(tech_support_data['email'], "email@email.com")


class SubscribeFormTests(TestCase):
    """
    Test for SubscribeFormTests
    """

    def test_subscribe_form_valid_data(self):
        """
        Verify that form is submitted with valid data
        """
        subscribe_data = {"email": "email@email.com"}
        subscribe_form = SubscribeForm(subscribe_data)

        self.assertTrue(subscribe_form.is_valid())

    def test_subscribe_form_invalid_data(self):
        """
        Verify that form is not submitted with invalid data
        :return: errors
        """
        subscribe_data = {}
        expected_errors = {'email': [u'This field is required.']}
        subscribe_form = SubscribeForm(subscribe_data)

        self.assertFalse(subscribe_form.is_valid())
        self.assertEqual(subscribe_form.errors, expected_errors)


class EdxOfferFormTests(TestCase):
    """
    Test for EdxOfferFormTests
    """

    def test_edx_offer_form(self):
        """
         Verify that form is submitted with valid data
        """
        data = {
            'full_name': 'full_name',
            'email': 'email@email.com',
            'company': 'company',
            'title': 'title',
            'education': 'PHD',
            'comment': 'Test comment'
        }
        edx_offer_form = EdxOfferForm(data)

        self.assertTrue(edx_offer_form.is_valid())

    def test_edx_offer_form_email_valid(self):
        """
         Verify that if email pattern is incorrect form is not submitted
        :return: errors
        """
        data = {
            'full_name': 'full_name',
            'email': 'email.email@com',
            'company': 'company',
            'title': 'title',
            'education': 'PHD',
            'comment': 'Test comment'
        }
        expected_errors = {'email': [u'Enter a valid email address.']}
        edx_offer_form = EdxOfferForm(data)

        self.assertFalse(edx_offer_form.is_valid())
        self.assertEqual(edx_offer_form.errors, expected_errors)
