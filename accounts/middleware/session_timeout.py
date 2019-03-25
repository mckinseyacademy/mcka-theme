''' expire session after a set amount of time '''
from datetime import datetime, timedelta
from django.conf import settings
from accounts.logout import logout
from api_client.api_error import ApiError
from api_client.user_api import get_user_dict


def expire_session(request):
    request.session.pop('last_touch', None)
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

        if settings.MOBILE_APP_USER_AGENT in request.META.get('HTTP_USER_AGENT', []):
            timeout = getattr(settings, "MOBILE_APP_SESSION_TIMEOUT_SECONDS", None)
            last_touch = request.session.get('last_touch')
            if timeout and last_touch:
                time = datetime.utcnow() - last_touch
                if time > timedelta(seconds=settings.MOBILE_APP_SESSION_TIMEOUT_SECONDS):
                    return expire_session(request)
            return

        timeout = getattr(settings, "SESSION_TIMEOUT_SECONDS", None)
        last_touch = request.session.get('last_touch')

        if timeout and last_touch:
            time = datetime.utcnow() - last_touch
            if time > timedelta(seconds=settings.SESSION_TIMEOUT_SECONDS):
                return expire_session(request)

        request.session['last_touch'] = datetime.utcnow()

    def process_response(self, request, response):
        if settings.MOBILE_APP_USER_AGENT in request.META.get('HTTP_USER_AGENT', []):
            if not request.session.get('last_touch'):
                request.session['last_touch'] = datetime.utcnow()
                response.set_cookie(
                    'last_touch',
                    datetime.utcnow(),
                    domain=settings.LMS_SESSION_COOKIE_DOMAIN,
                    max_age=settings.SESSION_COOKIE_AGE,
                )
        else:
            response.set_cookie(
                'last_touch',
                request.session.get('last_touch'),
                domain=settings.LMS_SESSION_COOKIE_DOMAIN,
                max_age=settings.SESSION_COOKIE_AGE,
            )
        return response
