import ddt

from django.test import TestCase, override_settings, RequestFactory, Client
from django.core.urlresolvers import reverse

from main.middleware.allow_embed_url import AllowEmbedUrlMiddleware


ALLOW_EMBED_URL = 'https://example.com https://example2.com'


@ddt.ddt
class AllowEmbedUrlTest(TestCase):
    @override_settings(ALLOW_EMBED_URL=ALLOW_EMBED_URL)
    def test_details(self):

        middleware = AllowEmbedUrlMiddleware()

        factory = RequestFactory()
        request = factory.get('/')

        request.META['HTTP_REFERER'] = ALLOW_EMBED_URL

        middleware.process_request(request)

        client = Client()
        response = client.get(reverse('home'))

        middleware.process_response(request, response)

        self.assertEqual(middleware.is_scorm_shell, True)
        self.assertEqual(response['Content-Security-Policy'], 'frame-ancestors ' + ALLOW_EMBED_URL)
        self.assertEqual(response['X-Frame-Options'], 'ALLOW-FROM ' + ALLOW_EMBED_URL)

    @override_settings(ALLOW_EMBED_URL=ALLOW_EMBED_URL)
    @ddt.data(
        ('https://example.com/a/url/', True),
        ('https://abc.com/a/url', False),
        ('https://example2.com/a/url', True),
    )
    @ddt.unpack
    def test_by_referrer_cookie(self, referrer_url, is_scorm_shell):
        """
        tests middleware by referrer cookie
        """
        middleware = AllowEmbedUrlMiddleware()

        request = RequestFactory().get('/')
        request.COOKIES['referrer_url'] = referrer_url

        middleware.process_request(request)

        client = Client()
        response = client.get(reverse('home'))

        middleware.process_response(request, response)

        self.assertEqual(middleware.is_scorm_shell, is_scorm_shell)

        if is_scorm_shell:
            self.assertEqual(response['Content-Security-Policy'], 'frame-ancestors ' + ALLOW_EMBED_URL)
            self.assertEqual(response['X-Frame-Options'], 'ALLOW-FROM ' + ALLOW_EMBED_URL)

    @override_settings(ALLOW_EMBED_URL=ALLOW_EMBED_URL)
    @ddt.data(
        ('https://example.com/a/url/', True),
        ('https://abc.com/a/url', False),
        ('https://example2.com/a/url', True),
    )
    @ddt.unpack
    def test_in_allowed_embed_urls(self, referrer_url, expected):
        """
        test helper method for checking allowed urls
        """
        middleware = AllowEmbedUrlMiddleware()

        self.assertEqual(middleware.in_allowed_embed_urls(referrer_url), expected)