""" Tests for S3 private media storage class """

import unittest

import ddt

from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.conf import settings

from lib.utils import DottableDict
from util.s3_helpers import PrivateMediaStorageThroughApros
from util.unit_test_helpers import ApplyPatchMixin
from util.unit_test_helpers.common_mocked_objects import (
    mock_storage_save,
    TestUser
)
from api_client.group_api import PERMISSION_GROUPS


@ddt.ddt
class TestPrivateMediaStorageThroughApros(unittest.TestCase, ApplyPatchMixin):
    """
    Tests for secure media storage backend
    """
    def setUp(self):
        self.apply_patch(
            'util.tests.test_s3_helpers.PrivateMediaStorageThroughApros.save',
            new=mock_storage_save
        )

        self.user_group_api = self.apply_patch(
            'lib.authorization.user_api.get_user_groups'
        )

        self.group_api = self.apply_patch(
            'lib.authorization.group_api.get_groups_of_type'
        )
        self.group_api.return_value = [DottableDict({'id': 1, 'name': PERMISSION_GROUPS.MCKA_ADMIN})]

        self.storage = PrivateMediaStorageThroughApros()
        self.csv_exports_dir = settings.EXPORT_STATS_DIR
        self.test_content = ContentFile('Hello World!')
        self.test_user = TestUser(is_staff=False, user_id=123, email='mail@example.com')

    def test_resource_url(self):
        """
        Tests that file's url is an Apros endpoint
        """
        file_path = '{}/{}'.format(self.csv_exports_dir, 'test_file.txt')
        storage_path = self.storage.save(file_path, self.test_content)
        url = self.storage.url(storage_path)

        # tha url generated from `storage.url()` and `private_storage` url should match
        self.assertEqual(url, reverse('private_storage', kwargs={'path': storage_path}))

    @ddt.data(
        ([], False),
        ([
            DottableDict({'id': 1, 'name': PERMISSION_GROUPS.MCKA_ADMIN}),
            DottableDict({'id': 2, 'name': PERMISSION_GROUPS.INTERNAL_ADMIN}),
            DottableDict({'id': 3, 'name': PERMISSION_GROUPS.MCKA_SUBADMIN}),
            DottableDict({'id': 4, 'name': PERMISSION_GROUPS.COMPANY_ADMIN}),
         ], True)  # only admins accessible
    )
    @ddt.unpack
    def test_access_method(self, permission_groups, is_accessible):
        """
        Tests that access check is applied
        """
        file_path = '{}/{}'.format(self.csv_exports_dir, 'test_file.txt')
        storage_path = self.storage.save(file_path, self.test_content)

        self.user_group_api.return_value = permission_groups
        can_access = self.storage.can_access(storage_path, self.test_user)

        self.assertEqual(can_access, is_accessible)
