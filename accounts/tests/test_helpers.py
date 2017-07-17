"""
Tests for helpers.py module
"""
from ddt import ddt, data

from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse

from accounts.models import UserActivation
from accounts.helpers import (
    get_user_activation_links, create_activation_url, TestUser,
    get_complete_country_name,
    is_mobile_user_agent
)


@ddt
class AccountActivationHelpersTest(TestCase):
    """
    Test cases for activation related helper methods
    """
    def setUp(self):
        """
        Sets up the test case
        """
        super(AccountActivationHelpersTest, self).setUp()
        self.users = [
            TestUser(user_id=x, email='user_{}@example.com'.format(x))
            for x in xrange(5)
        ]

        # ToDo: use factory boy etc for object creation
        self.activation_records = [
            UserActivation.user_activation(user)
            for user in self.users
        ]

    def test_get_activation_links(self):
        """
        Tests retrieval of activation links
        """
        activation_links = get_user_activation_links(user_ids=[user.id for user in self.users])

        self.assertEqual(len(activation_links), len(self.activation_records))

    @data('', 'http://base.xyz')
    def test_create_activation_url(self, base_url):
        """
        Tests creating activation url
        """
        activation_code = self.activation_records[0].activation_key
        created_activation_url = create_activation_url(activation_code, base_url=base_url)

        activation_url = reverse('activate', kwargs={'activation_code': activation_code})

        self.assertTrue(created_activation_url == activation_url or activation_url in created_activation_url)

    def test_get_full_country_name(self):
        """
        Tests getting full country name
        """
        full_country_name = 'Italy'
        short_form = 'IT'

        self.assertEqual(get_complete_country_name(short_form), full_country_name)


class MobileUserAgentHelperTest(TestCase):
    """
    Test cases for request user agent helper method
    """
    def test_is_mobile_user_agent_empty_user_agent(self):
        """
        test is_mobile_user_agent_mobile method with empty user agent request
        """
        request = RequestFactory(HTTP_USER_AGENT='').get('')
        self.assertFalse(is_mobile_user_agent(request))

    def test_is_mobile_user_agent_mobile_user_agent(self):
        """
        test is_mobile_user_agent_mobile method with mobile user agent request
        """
        iphone_ua_string = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
        request = RequestFactory(HTTP_USER_AGENT=iphone_ua_string).get('')
        self.assertTrue(is_mobile_user_agent(request))
