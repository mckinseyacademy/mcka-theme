import copy
from admin.models import internal_admin_role_granted, internal_admin_role_revoked

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
        USER_ROLES.TA: PERMISSION_GROUPS.MCKA_TA,
        USER_ROLES.OBSERVER: PERMISSION_GROUPS.MCKA_OBSERVER
    }

    def __init__(self, user_id):
        self.permission_groups = group_api.get_groups_of_type(PERMISSION_TYPE)
        self.current_permissions = [pg.name for pg in user_api.get_user_groups(user_id, PERMISSION_TYPE)]
        self.courses = course_api.get_course_list()
        self.user_roles = user_api.get_user_roles(user_id)
        self.user_id = user_id

    def add_course_role(self, course_id, role):
        per_course_roles = [{"course_id": p.course_id, "role": p.role}
                            for p in self.user_roles if p.course_id != course_id and p.role != role]
        per_course_roles.append({
            "course_id": course_id,
            "role": role,
        })
        self.save(copy.copy(self.current_permissions), per_course_roles)

    def remove_course_role(self, course_id, role):
        per_course_roles = [{"course_id": p.course_id, "role": p.role}
                            for p in self.user_roles if p.course_id != course_id and p.role != role]
        role_permission = self.permission_for_role.get(course_role['role'], None)
        new_permissions = [perm for perm in self.current_permissions if perm != role_permission]
        self.save(new_permissions, per_course_roles)

    def save(self, new_permissions, per_course_roles):
        try:
            # update user roles
            if per_course_roles:
                user_api.update_user_roles(self.user_id, {'roles': per_course_roles,
                                                          'ignore_roles': settings.IGNORE_ROLES})
            else:
                # empty list - delete all roles
                for role in self.user_roles:
                    user_api.delete_user_role(self.user_id, role.course_id, role.role)

            for course_role in per_course_roles:
                permission = self.permission_for_role.get(course_role['role'], None)
                if permission:
                    new_permissions.append(permission)

            # get unique items
            new_permissions = set(new_permissions)

            # update permissions
            for permission in new_permissions:
                if permission not in self.current_permissions:
                    self.add_permission(permission)

            for permission in self.current_permissions:
                if permission not in new_permissions:
                    self.remove_permission(permission)

        except ApiError as err:
            raise PermissionSaveError(str(err))

    def get_group_id(self, permission_name):
        return next((g.id for g in self.permission_groups if g.name == permission_name), None)

    def add_permission(self, permission_name):
        group_id = self.get_group_id(permission_name)
        if group_id:
            group_api.add_user_to_group(self.user_id, group_id)
            internal_admin_role_granted.send(user_id=self.user_id)

    def remove_permission(self, permission_name):
        group_id = self.get_group_id(permission_name)
        if group_id:
            group_api.remove_user_from_group(self.user_id, group_id)
            internal_admin_role_revoked.send(user_id=self.user_id)
