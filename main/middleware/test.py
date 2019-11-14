import sys

import ddt

from django.test import TestCase, override_settings, RequestFactory, Client
from django.core.urlresolvers import reverse

from main.middleware.allow_embed_url import AllowEmbedUrlMiddleware
from django_assets import env as assets_env
from mcka_apros import settings

ALLOW_EMBED_URL = 'https://example.com https://example2.com'


@ddt.ddt
class AllowEmbedUrlTest(TestCase):
    # override_settings decorator doesn't do proper cleanup, so tests based on assets fails in some envs
    # added settings clean up hack to fix the issue
    def setUp(self):
        super(AllowEmbedUrlTest, self).setUp()
        self.settings_override = override_settings(**{'ALLOW_EMBED_URL': ALLOW_EMBED_URL})
        self.settings_override.enable()

    def tearDown(self):
        super(AllowEmbedUrlTest, self).tearDown()
        self.settings_override.disable()
        assets_env.reset()
        assets_env._ASSETS_LOADED = False
        for name in settings.INSTALLED_APPS:
            assets_module = name + '.assets'
            if assets_module in sys.modules:
                del sys.modules[assets_module]

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
        self.assertEqual(response['X-Frame-Options'], 'ALLOW-FROM ' + 'https://example.com')

    @ddt.data(
        ('https://example.com/a/url/', True, 'ALLOW-FROM https://example.com'),
        ('https://abc.com/a/url', False, 'SAMEORIGIN'),
        ('https://example2.com/a/url', True, 'ALLOW-FROM https://example2.com'),
    )
    @ddt.unpack
    def test_by_referrer_cookie(self, referrer_url, is_scorm_shell, expected_x_frame_option):
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
            self.assertEqual(response['X-Frame-Options'], expected_x_frame_option)

    @ddt.data(
        ('https://example.com/a/url/', 'https://example.com'),
        ('https://abc.com/a/url', False),
        ('https://example2.com/a/url', 'https://example2.com'),
    )
    @ddt.unpack
    def test_get_matched_allowed_embed_url(self, referrer_url, expected):
        """
        test helper method for checking allowed urls
        """
        middleware = AllowEmbedUrlMiddleware()

        self.assertEqual(middleware.get_matched_allowed_embed_url(referrer_url), expected)
