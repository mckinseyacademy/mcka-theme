import ddt

from django.test import TestCase
from marketing.forms import TechSupportForm, SubscribeForm
from util.unit_test_helpers import AprosTestingClient
from django.core.urlresolvers import reverse
from mock import mock


@ddt.ddt
class MarketingViewTests(TestCase):
    """
       Test for the Marketing Views.
       """
    client_class = AprosTestingClient

    def setUp(self):
        """
        Setup marketing view test
        """
        super(MarketingViewTests, self).setUp()

    def test_contact(self):
        """
        Test viewing the contact that redirects to home page
        """

        url = reverse('contact')
        data = {'tech_support_form': TechSupportForm, 'subscribe_form': SubscribeForm}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    @ddt.data(
        'programs',
        'about',
        'experience',
        'edxoffer',
        'fblf',
    )
    def test_infer_default_navigation_with_page(self, page_name):
        """
        Test viewing the infer_default_navigation with differnet pages
        so it redirects to the home page
        """
        url = reverse('infer_default_navigation', kwargs={'page_name': page_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_infer_default_navigation_without_template(self):
        """
        Test the infer_default_navigation view with no template so it
        returns 404.
        """
        url = reverse('infer_default_navigation', kwargs={'page_name': ''})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_style_guide(self):
        """
        Test viewing the style guide
        """
        style_guide_url = reverse('styleguide')
        response = self.client.get(style_guide_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'marketing/styleguide.haml')

    def test_support(self):
        """
        If we try to post with an valid support form data pattern,
        then we'll be redirected to contact page.
        """
        tech_support_data = {
            "type": "problem",
            "name": "name",
            "comment": "Some detail",
            "email": "email@email.com",
        }

        support_url = reverse('support')
        with mock.patch('marketing.forms.TechSupportForm.save'):
            response = self.client.post(support_url, tech_support_data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/contact/')

    def test_subscribe(self):
        """
        If we try to post with an valid subscribe form data pattern,
        then we'll be redirected to contact page.
        """
        tech_subscribe_data = {
            "email": "email@email.com",
        }
        subscribe_url = reverse('subscribe')
        with mock.patch('marketing.forms.SubscribeForm.save'):
            response = self.client.post(subscribe_url, tech_subscribe_data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/contact/')

    def test_edx_offer(self):
        """
        Test viewing the edx offer that redirects to home page
        """
        edx_offer_url = reverse('edxoffer')
        response = self.client.get(edx_offer_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
