import time
from django.test import TestCase
from django.core.cache import cache

from accounts.tests.utils import ApplyPatchMixin
from admin.permissions import Permissions
from lib.utils import DottableDict

permission_groups = [
    DottableDict({
        "id": 1,
        "url": "http://0.0.0.0:8000/api/server/groups/1/",
        "name": "mcka_role_company_admin",
        "type": "permission",
        "data": {}
    }),
    DottableDict({
        "id": 3,
        "url": "http://0.0.0.0:8000/api/server/groups/3/",
        "name": "mcka_role_mcka_admin",
        "type": "permission",
        "data": {}
    }),
    DottableDict({
        "id": 2,
        "url": "http://0.0.0.0:8000/api/server/groups/2/",
        "name": "mcka_role_client_observer",
        "type": "permission",
        "data": {}
    }),
    DottableDict({
        "id": 4,
        "url": "http://0.0.0.0:8000/api/server/groups/4/",
        "name": "mcka_role_mcka_ta",
        "type": "permission",
        "data": {}
    }),
    DottableDict({
        "id": 5,
        "url": "http://0.0.0.0:8000/api/server/groups/5/",
        "name": "mcka_role_internal_admin",
        "type": "permission",
        "data": {}
    }),

]

user_groups = [
    DottableDict({
        "id": 1,
        "url": "http://0.0.0.0:8000/api/server/groups/1/",
        "name": "mcka_role_company_admin",
        "type": "permission",
        "data": {}
    }),
    DottableDict({
        "id": 3,
        "url": "http://0.0.0.0:8000/api/server/groups/3/",
        "name": "mcka_role_mcka_admin",
        "type": "permission",
        "data": {}
    }),
    DottableDict({
        "id": 2,
        "url": "http://0.0.0.0:8000/api/server/groups/2/",
        "name": "mcka_role_client_observer",
        "type": "permission",
        "data": {}
    }),
    DottableDict({
        "id": 4,
        "url": "http://0.0.0.0:8000/api/server/groups/4/",
        "name": "mcka_role_mcka_ta",
        "type": "permission",
        "data": {}
    }),
]

courses_list = [
    DottableDict({
        "id": "123/1234/1234",
        "name": "problem builder temp",
        "category": "course",
        "number": "1234",
        "org": "123",
        "uri": "http://0.0.0.0:8000/api/server/courses/123/1234/1234",
        "course_image_url": "/c4x/123/1234/asset/images_course_image.jpg",
        "mobile_available": 'false',
        "due": 'null',
        "start": "2018-01-01T00:00:00Z",
        "end": 'null'
    }),
    DottableDict({
        "id": "arbisoft/1/1",
        "name": "Int - Regresion - 10 jan 2018",
        "category": "course",
        "number": "1",
        "org": "arbisoft",
        "uri": "http://0.0.0.0:8000/api/server/courses/arbisoft/1/1",
        "course_image_url": "/c4x/arbisoft/1/asset/images_course_image.jpg",
        "mobile_available": 'true',
        "due": 'null',
        "start": "2018-01-01T00:00:00Z",
        "end": 'null'
    })
]

user_roles = [
    DottableDict({
        "course_id": "123/1234/1234",
        "role": "staff"
    }),
    DottableDict({
        "course_id": "arbisoft/1/1",
        "role": "participant"
    })
]

company_admin_list = [
    {
        'id': '1',
        'name': 'testing'
    }
]

organization_list = [
    DottableDict({'id': 1}),
    DottableDict({'id': 2})
]


class TestPermissions(TestCase, ApplyPatchMixin):
    def setUp(self):
        self.group_api = self.apply_patch('admin.permissions.group_api')
        self.user_api = self.apply_patch('admin.permissions.user_api')
        self.course_api = self.apply_patch('admin.permissions.course_api')
        self.organization_api = self.apply_patch('admin.permissions.organization_api')

        self.group_api.get_groups_of_type.return_value = permission_groups
        self.user_api.get_user_groups.return_value = user_groups
        self.user_api.get_user_roles.return_value = user_roles
        self.user_api.get_user_organizations.return_value = organization_list
        self.course_api.get_course_list.return_value = courses_list
        self.organization_api.get_users_from_organization_group.return_value = company_admin_list
        self.organization_api.get_all_organization_groups.return_value = user_groups[1:]
        self.organization_api.add_group_to_organization.return_value = True

        self.user_api.update_user_roles = self._mock_update_user_roles
        self.group_api.add_users_to_group = self._mock_add_users_to_group
        self.organization_api.add_user_to_organization = self._mock_add_user_to_organization
        self.organization_api.remove_users_from_organization = self._mock_remove_users_from_organization

        self.permission = Permissions(1)

    def test_get_course_list_or_cached(self):
        courses = self.permission.get_course_list_or_cached()
        self.assertEqual(courses, courses_list)
        self.permission.CACHE_EXPIRE_TIME = -1
        courses = self.permission.get_course_list_or_cached()
        self.assertEqual(courses, courses_list)
        cache.delete('course_list_cached_last_update_time')
        courses = self.permission.get_course_list_or_cached()
        self.assertEqual(courses, courses_list)
        course_list_cached_last_update_time = int(cache.get('course_list_cached_last_update_time'))
        time_now = int(time.time())
        self.assertEqual(course_list_cached_last_update_time, time_now)

    def test_get_groups_of_type_permission_cached(self):
        result = self.permission.get_groups_of_type_permission_cached()
        self.assertEqual(result, permission_groups)
        self.assertEqual(result, cache.get('permission_groups_cached'))

    def test_add_course_role(self):
        self.permission.add_course_role('testing_id', 'assistant')
        self.assertTrue('mcka_role_mcka_ta' in self.permission.current_permissions)

    def _mock_update_user_roles(self, user_id, new_roles):
        self.permission.user_roles = [DottableDict(role) for role in new_roles['roles']]

    def _mock_add_users_to_group(self, user_list, group_id):
        permission_group = [permission_group for permission_group in permission_groups if
                            group_id == permission_group.id]
        if permission_group[0]:
            self.permission.current_permissions.append(permission_group[0])

    def _mock_add_user_to_organization(self, organization_id, user_id):
        organization_list.append(DottableDict({'id': organization_id}))

    def _mock_remove_users_from_organization(self, organization_id, user_id):
        organization_list.remove(DottableDict({'id': organization_id}))

    def test_remove_all_course_roles(self):
        self.permission.remove_all_course_roles('123/1234/1234')
        previous_role = user_roles[0]
        self.assertFalse(previous_role in self.permission.user_roles)

    def test_update_course_role(self):
        self.permission.update_course_role('arbisoft/1/1', 'assistant')
        self.assertEqual(self.permission.user_roles[1]['role'], 'assistant')
        result = self.permission.update_course_role('arbisoft/1/1', 'assistant')
        self.assertIsNone(result)

    def test_update_courses_roles_list(self):
        new_user_roles = [
            {
                "course_id": "123/1234/1234",
                "role": "assistant"
            },
            {
                "course_id": "arbisoft/1/1",
                "role": "staff"
            }
        ]
        self.permission.update_courses_roles_list(new_user_roles)
        self.assertEqual(self.permission.user_roles, new_user_roles)

    def test_add_permission(self):
        internal_admin = DottableDict({
            "id": 5,
            "url": "http://0.0.0.0:8000/api/server/groups/5/",
            "name": "mcka_role_internal_admin",
            "type": "permission",
            "data": {}
        })
        self.permission.add_permission('mcka_role_internal_admin')
        self.assertTrue(internal_admin in self.permission.current_permissions)

    def test_check_if_company_admin(self):
        self.assertTrue(self.permission.check_if_company_admin(1))
        self.permission.user_id = 2
        self.assertFalse(self.permission.check_if_company_admin(1))

    def test_get_all_user_organizations_with_permissions(self):
        result_user = self.permission.get_all_user_organizations_with_permissions()

        self.assertEqual(result_user.get('company_num'), 2)
        self.assertEqual(result_user.get('company_ids'), [1, 2])
        self.assertEqual(result_user.get('main_company'), [{'id': 1}])
        self.assertEqual(
            result_user.get('mcka_role_company_admin'),
            [{'id': 1}, {'id': 2}]
        )

        self.organization_api.get_users_from_organization_group.return_value = [
            DottableDict({'id': '3', 'name': 'testing'})]

        result_user = self.permission.get_all_user_organizations_with_permissions()

        self.assertEqual(result_user.get('company_num'), 2)
        self.assertEqual(result_user.get('company_ids'), [1, 2])
        self.assertEqual(result_user.get('main_company'), [{'id': 1}, {'id': 2}])
        self.assertEqual(result_user.get('mcka_role_company_admin'), [])

        self.permission.permission_groups = permission_groups[1:]
        result_user = self.permission.get_all_user_organizations_with_permissions()

        self.assertEqual(result_user.get('company_num'), 1)
        self.assertEqual(result_user.get('company_ids'), [1])
        self.assertEqual(result_user.get('main_company'), [{'id': 1}])
        self.assertEqual(result_user.get('mcka_role_company_admin'), [])

    def test_add_company_admin_permissions(self):
        self.permission.current_permissions = user_groups[1:]
        self.permission.add_company_admin_permissions([2, 3])
        user_orgs = self.permission.get_all_user_organizations_with_permissions()
        self.assertTrue({'id': 3} in user_orgs['mcka_role_company_admin'])
        self.assertEqual(user_orgs['company_num'], 3)
        self.assertEqual(user_orgs['company_ids'], [1, 2, 3])
        self.assertEqual(len(self.permission.current_permissions), len(user_groups))
        organization_list.remove(DottableDict({'id': 3}))

    def test_remove_company_admin_permission(self):
        self.permission.remove_company_admin_permission([2])
        user_orgs = self.permission.get_all_user_organizations_with_permissions()
        self.assertTrue({'id': 2} not in user_orgs['mcka_role_company_admin'])
        self.assertEqual(user_orgs['company_num'], 1)
        self.assertEqual(user_orgs['company_ids'], [1])
        organization_list.append(DottableDict({'id': 2}))

    def test_update_company_admin_permissions(self):
        self.permission.update_company_admin_permissions([1, 3])
        user_orgs = self.permission.get_all_user_organizations_with_permissions()
        self.assertTrue({'id': 2} not in user_orgs['mcka_role_company_admin'])
        self.assertTrue({'id': 3} in user_orgs['mcka_role_company_admin'])
        self.assertEqual(user_orgs['company_num'], 2)
        self.assertEqual(user_orgs['company_ids'], [1, 3])
        organization_list.remove(DottableDict({'id': 3}))
        organization_list.append(DottableDict({'id': 2}))

    def test_has_grant_rights(self):
        result = self.permission.has_grant_rights('mcka_role_company_admin')
        self.assertTrue(result)
        result = self.permission.has_grant_rights('instructor')
        self.assertFalse(result)
