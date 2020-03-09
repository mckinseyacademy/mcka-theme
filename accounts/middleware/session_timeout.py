''' expire session after a set amount of time '''
from datetime import datetime, timedelta
from django.conf import settings
from accounts.logout import logout
from api_client.api_error import ApiError
from api_client.user_api import get_user_dict


def expire_session(request):
    request.session.pop('last_touch', None)
    logout(request)


class SessionTimeout:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not request.user.is_authenticated:
            # Can't log out if not logged in
            return self.get_response(request)

        try:
            # Log user out if deleted
            get_user_dict(request.user.id)
        except ApiError:
            expire_session(request)
            return self.get_response(request)

        if settings.MOBILE_APP_USER_AGENT in request.META.get('HTTP_USER_AGENT', []):
            timeout = getattr(settings, "MOBILE_APP_SESSION_TIMEOUT_SECONDS", None)
            last_touch = request.session.get('last_touch')
            if timeout and last_touch:
                time = datetime.utcnow() - last_touch
                if time > timedelta(seconds=settings.MOBILE_APP_SESSION_TIMEOUT_SECONDS):
                    expire_session(request)
                    return self.get_response(request)
            return self.get_response(request)

        timeout = getattr(settings, "SESSION_TIMEOUT_SECONDS", None)
        last_touch = request.session.get('last_touch')

        if timeout and last_touch:
            time = datetime.utcnow() - last_touch
            if time > timedelta(seconds=settings.SESSION_TIMEOUT_SECONDS):
                expire_session(request)
                return self.get_response(request)

        request.session['last_touch'] = datetime.utcnow()

        response = self.get_response(request)

        if settings.MOBILE_APP_USER_AGENT in request.META.get('HTTP_USER_AGENT', []):
            if not request.session.get('last_touch'):
                request.session['last_touch'] = datetime.utcnow()
        else:
            # Offset in seconds to support events using this cookie's value on timeout
            offset = 7
            response.set_cookie(
                'last_touch',
                request.session.get('last_touch'),
                domain=settings.LMS_SESSION_COOKIE_DOMAIN,
                expires=settings.SESSION_TIMEOUT_SECONDS + offset,
            )
        return response
