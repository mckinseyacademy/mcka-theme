""" Tests for S3 private media storage class """

import unittest

import ddt

from django.core.files.base import ContentFile
from django.urls import reverse
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

        self.apply_patch(
            'util.s3_helpers.export_stats_permission_check',
            new=self._mocked_export_stats_check_method
        )

        self.user_group_api = self.apply_patch(
            'lib.authorization.user_api.get_user_groups'
        )

        self.user_group_api.return_value = [
            DottableDict({'id': 1, 'name': PERMISSION_GROUPS.MCKA_ADMIN}),
            DottableDict({'id': 2, 'name': PERMISSION_GROUPS.INTERNAL_ADMIN}),
            DottableDict({'id': 3, 'name': PERMISSION_GROUPS.MCKA_SUBADMIN}),
            DottableDict({'id': 4, 'name': PERMISSION_GROUPS.COMPANY_ADMIN}),
        ]

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
        (None, 'org_101/cs_101/2018_T1', PERMISSION_GROUPS.MCKA_ADMIN, True),  # Uber admin can access all paths
        ('1', 'org_101/cs_102/2018_T1', PERMISSION_GROUPS.MCKA_ADMIN, True),
        (None, 'org_101/cs_101/2018_T1', PERMISSION_GROUPS.INTERNAL_ADMIN, True),  # internal course file
        (None, 'org_101/cs_102/2018_T1', PERMISSION_GROUPS.INTERNAL_ADMIN, False),  # non-internal course file
        ('1', 'org_101/cs_102/2018_T1', PERMISSION_GROUPS.COMPANY_ADMIN, True),  # belongs to company
        ('2', 'org_101/cs_102/2018_T1', PERMISSION_GROUPS.COMPANY_ADMIN, False),  # non-company file
        (None, 'org_101/cs_102/2018_T1', PERMISSION_GROUPS.COMPANY_ADMIN, False),
    )
    @ddt.unpack
    def test_access_method(self, company_id, course_id, user_role, is_accessible):
        """
        Tests that access check is applied
        """
        storage_path = self.csv_exports_dir
        if company_id:
            storage_path += '/' + company_id

        file_path = '{}/{}/'.format(storage_path, course_id.replace('/', '__'), 'test_file.csv')
        storage_path = self.storage.save(file_path, self.test_content)
        self.test_user.user_role = user_role

        can_access = self.storage.can_access(storage_path, self.test_user)

        self.assertEqual(can_access, is_accessible)

    def _mocked_export_stats_check_method(self, user, company_id, course_id):
        """
        Method mocked to avoid mocking lot of APIs involved
        """
        if user.is_company_admin:
            if not company_id or int(company_id) not in [1]:
                return False

            company_courses = ['org_101/cs_102/2018_T1']

            if course_id not in company_courses:
                return False
        elif user.is_internal_admin:
            return course_id in ['org_101/cs_101/2018_T1']

        return True
