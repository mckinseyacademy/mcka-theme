from django.http import HttpRequest
from django.test import TestCase

from util.url_helpers import get_referer_from_request


class TestGetRefererFromRequest(TestCase):
    """These validate whether HTTP_REFERER set in request header or not"""
    def test_get_referer_from_request_when_referer_is_set(self):
        """Test when referer is set"""
        request = HttpRequest()
        request.META['HTTP_REFERER'] = 'mckinseyacademy.com'
        self.assertEqual(get_referer_from_request(request), 'mckinseyacademy.com')

    def test_get_referer_from_request_when_referer_is_not_set(self):
        """Test when referer not set"""
        request = HttpRequest()
        request.META['HTTP_REFERER'] = ''
        self.assertIsNone(get_referer_from_request(request))
