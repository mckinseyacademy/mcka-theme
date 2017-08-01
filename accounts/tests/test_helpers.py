"""
Tests for helpers.py module
"""
from ddt import ddt, data

from django.test import TestCase
from django.core.urlresolvers import reverse

from accounts.models import UserActivation
from accounts.helpers import (
    get_user_activation_links, create_activation_url, TestUser,
    get_complete_country_name,
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