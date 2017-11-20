# pylint: disable=missing-docstring
from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from django.conf import settings
from django.core.cache import cache
from mock import patch
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


HTTP_HEADERS = {
    "Accept": "application/json",
}
OAUTH2_TOKEN_CACHE_KEY = 'oauth2-openedx-client-credentials-token'

log = logging.getLogger(__name__)


def is_secure_transport(uri):
    """
    Check if the URL is using HTTPS _or_ is a localhost URL (in which case
    we can still use insecure HTTP for API calls, since it's not going over
    any network).
    """
    uri_lower = uri.lower()
    safe_prefixes = settings.OAUTH2_SAFE_URL_PREFIXES
    if settings.DEBUG:
        safe_prefixes.append('http://lms.mcka.local/')  # Used on devstacks
    return any(uri_lower.startswith(prefix) for prefix in safe_prefixes)


def get_oauth2_session():
    """
    Returns an oauth2-enabled requests session.
    """
    with MockableSecureTransport():
        oauth2_client = BackendApplicationClient(client_id=settings.OAUTH2_OPENEDX_CLIENT_ID)
        session = AprosOAuth2Session(client=oauth2_client)
        session.headers = HTTP_HEADERS
        return session


class AprosOAuth2Session(OAuth2Session):
    def request(self, *args, **kwargs):  # pylint: disable=arguments-differ
        with MockableSecureTransport():
            session = super(AprosOAuth2Session, self)
            response = session.request(*args, **kwargs)
            if response.status_code == 401:
                _authorize(self)
                response = session.request(headers=HTTP_HEADERS, *args, **kwargs)
        return response
    request.__doc__ = OAuth2Session.request.__doc__


class MockableSecureTransport(object):
    """
    In both dev and production, we often call APIs on localhost over HTTP,
    which we want to allow, while still guarding against calling external
    APIs over insecure HTTP.
    """
    def __init__(self):
        self.mock1 = patch('oauthlib.oauth2.rfc6749.clients.base.is_secure_transport', new=is_secure_transport)
        self.mock2 = patch('requests_oauthlib.oauth2_session.is_secure_transport', new=is_secure_transport)

    def start(self):
        self.mock1.start()
        self.mock2.start()

    def stop(self):
        self.mock1.stop()
        self.mock2.stop()

    def __enter__(self):
        self.start()

    def __exit__(self, *args):
        self.stop()


def _authorize(session):
    if session.authorized:  # We have an access token but it doesn't work
        _request_new_token(session)
    else:  # Try the existing token
        token = _retrieve_existing_token(session)
        if token:
            session.token = token
        else:
            _request_new_token(session)
    return session.token


def _retrieve_existing_token(session):  # pylint: disable=unused-argument
    return cache.get(OAUTH2_TOKEN_CACHE_KEY)


def _request_new_token(session):
    token = session.fetch_token(
        token_url='{}/oauth2/access_token/'.format(settings.API_SERVER_ADDRESS),
        client_id=settings.OAUTH2_OPENEDX_CLIENT_ID,
        client_secret=settings.OAUTH2_OPENEDX_CLIENT_SECRET
    )
    cache.set(OAUTH2_TOKEN_CACHE_KEY, token)
    return token
