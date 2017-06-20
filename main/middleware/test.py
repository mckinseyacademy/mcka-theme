from django.test import TestCase, override_settings, RequestFactory, Client
from accounts.views import home
from django.core.urlresolvers import reverse
from main.middleware.allow_embed_url import AllowEmbedUrlMiddleware

ALLOW_EMBED_URL = 'https://example.com'

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

        middleware.process_response(request,response)

        self.assertEqual(middleware.is_scorm_shell, True)
        self.assertEqual(response['Content-Security-Policy'], 'frame-ancestors ' + ALLOW_EMBED_URL)
        self.assertEqual(response['X-Frame-Options'], 'ALLOW-FROM ' + ALLOW_EMBED_URL)
