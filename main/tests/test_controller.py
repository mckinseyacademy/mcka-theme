"""This file include all the tests for controller methods."""

from django.test import TestCase

from main.controller import get_android_app_manifest_json

from accounts.tests.utils import ApplyPatchMixin
from lib.utils import DottableDict


class AndroidAppBannerManifestJsonFileControllerTest(TestCase, ApplyPatchMixin):
    """
    Test cases for android mobile app related manifest.json file
    """

    def setUp(self):
        """
        Sets up the test case
        """
        super(AndroidAppBannerManifestJsonFileControllerTest, self).setUp()

        self.user_organizations = [
            DottableDict(
                id=17,
            )
        ]

        self.mobile_apps = {
            "org_name": "MCKA",
            "android_app_id": "com.example",
        }

        self.get_user_organizations = self.apply_patch(
            'api_client.user_api.get_user_organizations'
        )

        self.get_mobile_apps_id = self.apply_patch(
            'accounts.controller.get_mobile_apps_id'
        )

    def test_has_android_app_mobile_id(self):
        """
        Tests user_android_mobile_app_id helper method when user has android mobile app id
        """
        user_id = 4

        self.get_user_organizations.return_value = self.user_organizations
        self.get_mobile_apps_id.return_value = self.mobile_apps

        result = get_android_app_manifest_json(user_id)

        self.assertEqual(result['related_applications'][0]['id'], self.mobile_apps['android_app_id'])
        self.assertEqual(result['name'], self.mobile_apps['org_name'])

    def test_has_no_android_app_mobile_id(self):
        """
        Tests user_android_mobile_app_id helper method when user has android mobile app id
        """
        user_id = 4
        self.get_user_organizations.return_value = []
        self.get_mobile_apps_id.return_value = []

        result = get_android_app_manifest_json(user_id)

        self.assertEqual(result['related_applications'][0]['id'], None)
        self.assertEqual(result['name'], None)
