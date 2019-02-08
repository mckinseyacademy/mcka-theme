"""
Tests for utility methods in user agent helpers
"""
from django.test import TestCase
from django.test.client import RequestFactory

from ..user_agent_helpers import is_mobile_user_agent, is_ios, is_android, is_supported_mobile_device, _get_user_agent


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
        iphone_ua_string = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 ' \
                           '(KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
        request = RequestFactory(HTTP_USER_AGENT=iphone_ua_string).get('')
        self.assertTrue(is_mobile_user_agent(request))


class TestIsIOS(TestCase):
    """Test cases for ios user agent"""
    def test_is_ios_empty_user(self):
        """Test is_ios method with empty user agent"""
        request = RequestFactory(HTTP_USER_AGENT='')
        self.assertFalse(is_ios(request))

    def test_is_ios_non_empty_valid_user_agent(self):
        """Test is_ios method with valid user agent"""
        ua_string = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 ' \
                    '(KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
        request = RequestFactory(HTTP_USER_AGENT=ua_string).get('')
        self.assertTrue(is_mobile_user_agent(request))
        self.assertTrue(is_ios(request))

    def test_is_ios_non_empty_invalid_user_agent(self):
        """Test is_ios method with invalid user agent"""
        ua_string = 'Mozilla/5.0 (Linux; U; Android 4.1.1; en-gb; Build/KLP)' \
                    'AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30'
        request = RequestFactory(HTTP_USER_AGENT=ua_string).get('')
        self.assertTrue(is_mobile_user_agent(request))
        self.assertFalse(is_ios(request))


class TestIsAndroid(TestCase):
    """Test cases for android user agent"""
    def test_is_android_empty_user(self):
        """Test is_android method with empty user agent"""
        request = RequestFactory(HTTP_USER_AGENT='').get('')
        self.assertFalse(is_android(request))

    def test_is_android_non_empty_valid_user_agent(self):
        """Test is_android method with valid user agent"""
        ua_string = 'Mozilla/5.0 (Linux; U; Android 4.1.1; en-gb; Build/KLP)' \
                    'AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30'
        request = RequestFactory(HTTP_USER_AGENT=ua_string).get('')
        self.assertTrue(is_mobile_user_agent(request))
        self.assertTrue(is_android(request))

    def test_is_android_non_empty_invalid_user_agent(self):
        """Test is_android method with invalid user agent"""
        ua_string = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 ' \
                    '(KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
        request = RequestFactory(HTTP_USER_AGENT=ua_string).get('')
        self.assertTrue(is_mobile_user_agent(request))
        self.assertFalse(is_android(request))


class TestIsSupportedMobileDevice(TestCase):
    """Test cases for checking mobile device supported or not"""
    def test_is_supported_mobile_device_empty_agent(self):
        """Testing with empty user agent"""
        request = RequestFactory(HTTP_USER_AGENT='').get('')
        self.assertFalse(is_supported_mobile_device(request))

    def test_is_supported_mobile_device_non_empty_valid_agent(self):
        """Testing valid user agent"""
        ua_string = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 ' \
                    '(KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
        request = RequestFactory(HTTP_USER_AGENT=ua_string).get('')
        self.assertTrue(is_supported_mobile_device(request))

    def test_is_supported_mobile_device_non_empty_invalid_agent(self):
        """Testing with invalid user agent"""
        ua_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 ' \
                    '(KHTML, like Gecko) Version/8.0.7 Safari/600.7.12'
        request = RequestFactory(HTTP_USER_AGENT=ua_string).get('')
        self.assertFalse(is_supported_mobile_device(request))


class TestGetUser(TestCase):
    """Test Cases for _get_user_agent method"""
    def test_get_user_agent(self):
        request = RequestFactory()
        self.assertEqual(_get_user_agent(request), None)

    def test_get_user_agent_string(self):
        ua_string = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 ' \
                    '(KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
        request = RequestFactory(HTTP_USER_AGENT=ua_string).get('')
        self.assertTrue(_get_user_agent(request))
