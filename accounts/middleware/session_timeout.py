''' expire session after a set amount of time '''
from datetime import datetime, timedelta
from django.conf import settings
from accounts.logout import logout
from api_client.api_error import ApiError
from api_client.user_api import get_user_dict


def expire_session(request):
    if 'last_touch' in request.session:
        del request.session['last_touch']
    logout(request)


class SessionTimeout(object):

    def process_request(self, request):
        if not request.user.is_authenticated:
            # Can't log out if not logged in
            return

        try:
            # Log user out if deleted
            get_user_dict(request.user.id)
        except ApiError:
            return expire_session(request)

        timeout = getattr(settings, "SESSION_TIMEOUT_SECONDS", None)
        last_touch = request.session.get('last_touch')

        if timeout and last_touch:
            time = datetime.utcnow() - last_touch
            if time > timedelta(seconds=settings.SESSION_TIMEOUT_SECONDS):
                return expire_session(request)

        request.session['last_touch'] = datetime.utcnow()

    def process_response(self, request, response):
        response.set_cookie(
            'last_touch',
            request.session.get('last_touch'),
            domain=settings.LMS_SESSION_COOKIE_DOMAIN,
        )
        return response
