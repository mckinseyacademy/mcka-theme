from api_client import user_api, group_api, course_api
from api_client.user_api import USER_ROLES
from api_client.group_api import PERMISSION_GROUPS, PERMISSION_TYPE
from api_client.api_error import ApiError
from django.conf import settings


class PermissionSaveError(Exception):
    pass

class Permissions(object):
    ''' Handles loading and saving user permissions and roles '''

    permission_for_role = {
        USER_ROLES.STAFF: PERMISSION_GROUPS.MCKA_TA,
        USER_ROLES.OBSERVER: PERMISSION_GROUPS.MCKA_OBSERVER
    }

    def __init__(self, user_id):
        self.permission_groups = group_api.get_groups_of_type(PERMISSION_TYPE)
        self.user_permission_groups = user_api.get_user_groups(user_id, PERMISSION_TYPE)
        self.user_permissions = [pg.name for pg in self.user_permission_groups]
        self.courses = course_api.get_course_list()
        self.user_roles = user_api.get_user_roles(user_id)
        self.user_id = user_id

    def is_admin(self):
        return PERMISSION_GROUPS.MCKA_ADMIN in self.user_permissions

    def initial_data(self):
        data = {}
        data['admin'] = self.is_admin()
        for course in self.courses:
            data[course.id] = []
            for role in self.user_roles:
                if course.id == role.course_id:
                    data[course.id].append(role.role)
        return data

    def save(self, is_admin, per_course_roles):
        try:
            if per_course_roles:
                user_api.update_user_roles(self.user_id, {'roles': per_course_roles,
                                                          'ignore_roles': settings.IGNORE_ROLES})
            else:
                # empty list - delete all roles
                for role in self.user_roles:
                    user_api.delete_user_role(self.user_id, role.course_id, role.role)

            role_names = [r['role'] for r in per_course_roles]

            for key in USER_ROLES:
                permission = self.permission_for_role.get(USER_ROLES[key], None)
                if USER_ROLES[key] in role_names:
                    self.add_permission(permission)
                else:
                    self.remove_permission(permission)

            if is_admin:
                self.add_permission(PERMISSION_GROUPS.MCKA_ADMIN)
            else:
                self.remove_permission(PERMISSION_GROUPS.MCKA_ADMIN)

        except ApiError as err:
            raise PermissionSaveError(str(err))

    def get_group_id(self, permission_name):
        return next((g.id for g in self.permission_groups if g.name == permission_name), None)

    def add_permission(self, permission_name):
        if not permission_name in self.user_permissions:
            group_id = self.get_group_id(permission_name)
            if group_id:
                group_api.add_user_to_group(self.user_id, group_id)

    def remove_permission(self, permission_name):
        if permission_name in self.user_permissions:
            group_id = self.get_group_id(permission_name)
            if group_id:
                group_api.remove_user_from_group(self.user_id, group_id)

