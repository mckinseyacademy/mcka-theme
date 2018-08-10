from urlparse import urlparse

from django.conf import settings


class AllowEmbedUrlMiddleware(object):
    is_scorm_shell = False

    def process_request(self, request):
        self.is_scorm_shell = False

        if 'HTTP_REFERER' in request.META:
            referrer_url = request.META['HTTP_REFERER']
            self.is_scorm_shell = self.in_allowed_embed_urls(referrer_url)

    def process_response(self, request, response):
        referrer_url = request.COOKIES.get('referrer_url')

        if referrer_url:
            self.is_scorm_shell = self.in_allowed_embed_urls(referrer_url)

        if self.is_scorm_shell:
            response['Content-Security-Policy'] = 'frame-ancestors ' + settings.ALLOW_EMBED_URL
            response['X-Frame-Options'] = 'ALLOW-FROM ' + settings.ALLOW_EMBED_URL

        response.delete_cookie('referrer_url')

        return response

    def in_allowed_embed_urls(self, referrer_url):
        """
        checks if a domain is allowed to embed Apros in an iframe
        """
        # build list of allowed hosts from allowed URLs,
        # remove *'s for easy matching
        allowed_hosts = map(
            lambda url: urlparse(url).hostname.replace('*', ''),
            settings.ALLOW_EMBED_URL.split()
        )

        for allowed_host in allowed_hosts:
            if referrer_url.find(allowed_host) != -1:
                return True

        return False
