''' expire session after a set amount of time '''
from datetime import datetime, timedelta
from django.conf import settings
from accounts.logout import logout


class SessionTimeout(object):

    def process_request(self, request):
        if not request.user.is_authenticated:
            # Can't log out if not logged in
            return

        timeout = getattr(settings, "SESSION_TIMEOUT_SECONDS", None)
        last_touch = request.session.get('last_touch')

        if timeout and last_touch:
            time = datetime.now() - last_touch
            if time > timedelta(seconds=settings.SESSION_TIMEOUT_SECONDS):
                del request.session['last_touch']
                logout(request)
                return

        request.session['last_touch'] = datetime.now()

    def process_response(self, request, response):
        response.set_cookie(
            'last_touch',
            request.session.get('last_touch'),
            domain=settings.LMS_SESSION_COOKIE_DOMAIN,
        )
        return response
