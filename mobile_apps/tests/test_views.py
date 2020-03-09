"""
Tests for mobile_apps django app
"""
import os

from django.test import TestCase
from django.test.client import Client
from django.urls import reverse


class MobileAppViewTest(TestCase):
    """
    Test cases for app_associations app views
    """
    def setUp(self):
        """
        Setup app_associations app views test
        """
        super(MobileAppViewTest, self).setUp()
        self.client = Client()
        self.android_asset_links_file_name = 'assetlinks.json'
        self.ios_site_association_file_name = 'apple-app-site-association'

    def _assert_app_association_file_content(self, url, file_name):
        """
        Assert that content for app association file matches files in response
        """
        response = self.client.get(url)
        self.assertEqual(
            response.get('Content-Disposition'),
            'attachment; filename={}'.format(file_name)
        )
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'asset_links_files',
            file_name
        )
        with open(file_path) as app_associations_file:
            file_content = app_associations_file.read()
            self.assertEqual(file_content, response.content)

    def test_android_asset_links_file(self):
        """
        Test get android asset links file view
        """
        android_asset_links_file_url = reverse('android_asset_links_file')
        self._assert_app_association_file_content(
            android_asset_links_file_url,
            self.android_asset_links_file_name
        )

    def test_ios_site_association_file(self):
        """
        Test get ios site association file view
        """
        ios_site_association_file_url = reverse('ios_site_association_file')
        self._assert_app_association_file_content(
            ios_site_association_file_url,
            self.ios_site_association_file_name
        )
