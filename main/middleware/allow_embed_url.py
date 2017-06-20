from urlparse import urlparse

from django.conf import settings


class AllowEmbedUrlMiddleware(object):
    is_scorm_shell = False

    def process_request(self, request):
        # build list of allowed hosts from allowed URLs, remove *'s for easy matching
        allowed_hosts = map(
            lambda url: urlparse(url).hostname.replace('*', ''),
            settings.ALLOW_EMBED_URL.split()
        )

        if 'HTTP_REFERER' in request.META:
            referer_url = request.META['HTTP_REFERER']

            for allowed_host in allowed_hosts:
                if referer_url.find(allowed_host) != -1:
                    self.is_scorm_shell = True
                    break

    def process_response(self, request, response):
        if self.is_scorm_shell:
            response['Content-Security-Policy'] = 'frame-ancestors ' + settings.ALLOW_EMBED_URL
            response['X-Frame-Options'] = 'ALLOW-FROM ' + settings.ALLOW_EMBED_URL

        return response
