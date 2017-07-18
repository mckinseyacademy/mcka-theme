"""
Tests for utility methods in user agent helpers
"""
from django.test import TestCase
from django.test.client import RequestFactory

from ..user_agent_helpers import is_mobile_user_agent


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
