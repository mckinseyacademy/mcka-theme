from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware


class SessionMiddleware(SessionMiddleware):
    def process_response(self, request, response):
        response = super(SessionMiddleware, self).process_response(request, response)

        if settings.SESSION_COOKIE_NAME in response.cookies:
            response.cookies[settings.SESSION_COOKIE_NAME]['samesite'] = 'None'
        if settings.CSRF_COOKIE_NAME in response.cookies:
            response.cookies[settings.CSRF_COOKIE_NAME]['samesite'] = 'None'

        return response
