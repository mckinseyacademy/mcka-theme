import ddt
import httpretty
from django.conf import settings
from django.test import TestCase

from api_client.third_party_auth_api import THIRD_PARTY_AUTH_API, get_providers_by_login_id


@ddt.ddt
class TestThirdPartyAuthApi(TestCase):
    """
    Test the Third Party Auth API calls
    """
    DEPTH = 10
    RESPONSE_WITH_ASSOCIATIONS = """
    {
      "active": [
        {
          "provider_id": "saml-testshib",
          "name": "TestShib"
        }
      ]
    }
    """
    RESPONSE_WITHOUT_ASSOCIATIONS = """
    {
      "active": []
    }
    """

    def _setup_responses(self):
        data = [
            (200, 'sso-user', self.RESPONSE_WITH_ASSOCIATIONS),
            (200, 'sso-user@test.com', self.RESPONSE_WITH_ASSOCIATIONS),
            (200, 'non-sso-user', self.RESPONSE_WITHOUT_ASSOCIATIONS),
            (200, 'non-sso-user@test.com', self.RESPONSE_WITHOUT_ASSOCIATIONS),
            (404, 'invalid-user', '')
        ]
        for status, login_id, response in data:
            httpretty.register_uri(
                httpretty.GET,
                '{}/{}/users/{}'.format(
                    settings.API_SERVER_ADDRESS,
                    THIRD_PARTY_AUTH_API,
                    login_id,
                ),
                body=response,
                status=status,
                content_type='application/json',
            )

    @ddt.data('sso-user', 'sso-user@test.com')
    @httpretty.httprettified
    def test_get_providers_sso_user(self, login_id):
        self._setup_responses()
        providers = get_providers_by_login_id(login_id)
        self.assertEqual(len(providers), 1)
        self.assertEqual(providers[0].provider_id, 'saml-testshib')

    @ddt.data('non-sso-user', 'non-sso-user@test.com')
    @httpretty.httprettified
    def test_get_providers_nonsso_user(self, login_id):
        self._setup_responses()
        providers = get_providers_by_login_id(login_id)
        self.assertEqual(len(providers), 0)

    @httpretty.httprettified
    def test_get_providers_nonexistent_user(self):
        self._setup_responses()
        providers = get_providers_by_login_id('invalid-user')
        self.assertEqual(len(providers), 0)
