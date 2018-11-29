from django.test import TestCase

from api_client.http_request_methods import _get_cookies
from lib.utils import DottableDict
from accounts.middleware.thread_local import _threadlocal


class TestHttpRequestMethod(TestCase):
    """
    Tests for http request methods
    """
    def test_get_cookies_without_request_cookies(self):
        """
        Test _get_cookies method without any cookies in request
        """
        _threadlocal.request = None
        self.assertEqual(_get_cookies(), dict())

    def test_get_cookies_with_request_cookies(self):
        """
        Test that _get_cookies method returns dictionary of cookies in request
        """
        cookies = dict(sessionid='WE32fewhbwejbfwe', csrftoken='wkwjef2323jnnwefwWWQd')
        request = DottableDict({'COOKIES': cookies})
        _threadlocal.request = request
        self.assertEqual(_get_cookies(), cookies)
