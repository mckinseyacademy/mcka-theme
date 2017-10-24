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
    def __init__(self):
        self.mock1 = patch('oauthlib.oauth2.rfc6749.clients.base.is_secure_transport', return_value=True)
        self.mock2 = patch('requests_oauthlib.oauth2_session.is_secure_transport', return_value=True)

    def start(self):
        if settings.DEBUG:
            self.mock1.start()
            self.mock2.start()

    def stop(self):
        if settings.DEBUG:
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
        token_url='http://localhost:8000/oauth2/access_token/',
        client_id=settings.OAUTH2_OPENEDX_CLIENT_ID,
        client_secret=settings.OAUTH2_OPENEDX_CLIENT_SECRET
    )
    cache.set(OAUTH2_TOKEN_CACHE_KEY, token)
    return token
