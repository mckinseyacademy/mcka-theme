from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware


class SessionMiddleware(SessionMiddleware):
    def process_response(self, request, response):
        response = super(SessionMiddleware, self).process_response(request, response)

        if getattr(settings, 'ENVIRONMENT', '') != 'development':
            if settings.SESSION_COOKIE_NAME in response.cookies:
                response.cookies[settings.SESSION_COOKIE_NAME]['samesite'] = 'None'
                response.cookies[settings.SESSION_COOKIE_NAME]['secure'] = True
            if 'sessionid' in response.cookies:
                response.cookies['sessionid']['samesite'] = 'None'
                response.cookies['sessionid']['secure'] = True

        return response
