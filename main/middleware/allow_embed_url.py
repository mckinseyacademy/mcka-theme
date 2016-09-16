from django.conf import settings

class AllowEmbedUrlMiddleware(object):

    is_scorm_shell = False

    def process_request(self, request):
        if 'HTTP_REFERER' in request.META:
            host = request.META['HTTP_REFERER']
            if settings.ALLOW_EMBED_URL and settings.ALLOW_EMBED_URL in host:
                self.is_scorm_shell = True
        
    def process_response(self, request, response):
        if self.is_scorm_shell:
            response['Content-Security-Policy'] = 'frame-ancestors ' + settings.ALLOW_EMBED_URL
            response['X-Frame-Options'] = 'ALLOW FROM ' + settings.ALLOW_EMBED_URL
        return response
