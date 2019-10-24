from urllib.parse import urlparse

from django.conf import settings


class AllowEmbedUrlMiddleware(object):
    is_scorm_shell = False

    def process_request(self, request):
        self.is_scorm_shell = False

        if 'HTTP_REFERER' in request.META:
            referrer_url = request.META['HTTP_REFERER']
            self.is_scorm_shell = bool(self.get_matched_allowed_embed_url(referrer_url))

    def process_response(self, request, response):
        allowed_embed_url = None
        referrer_url = request.COOKIES.get('referrer_url') or request.META.get('HTTP_REFERER')

        if referrer_url:
            allowed_embed_url = self.get_matched_allowed_embed_url(referrer_url)
            self.is_scorm_shell = bool(allowed_embed_url)

        if self.is_scorm_shell:
            response['Content-Security-Policy'] = 'frame-ancestors ' + settings.ALLOW_EMBED_URL
            if allowed_embed_url:
                response['X-Frame-Options'] = 'ALLOW-FROM ' + allowed_embed_url
                response.set_cookie('referrer_url', allowed_embed_url, domain=settings.LMS_SESSION_COOKIE_DOMAIN)

        return response

    def get_matched_allowed_embed_url(self, referrer_url):
        """
        returns allowed_embed_url if a domain is allowed to embed Apros in an iframe
        """
        # build map of allowed hosts and allowed_urls from allowed URLs,
        # remove *'s for easy matching
        allowed_urls = settings.ALLOW_EMBED_URL.split()
        allowed_hosts = {urlparse(url).hostname.replace('*', ''): url for url in allowed_urls}
        matched_urls = [allowed_hosts[host] for host in allowed_hosts if host in referrer_url]
        return matched_urls[0] if matched_urls else False
