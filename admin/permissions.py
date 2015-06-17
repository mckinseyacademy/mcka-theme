import copy
import logging
from admin.models import (
    internal_admin_role_event, course_program_event, program_client_event, Client,
    ROLE_ACTIONS, ASSOCIATION_ACTIONS
)

from api_client import user_api, group_api, course_api, organization_api
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

    def __init__(self, user_id, ):
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
            print per_course_roles
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
            internal_admin_role_event.send(sender=self.__class__, user_id=self.user_id, action=ROLE_ACTIONS.GRANT)

    def remove_permission(self, permission_name):
        group_id = self.get_group_id(permission_name)
        if group_id:
            group_api.remove_user_from_group(self.user_id, group_id)
            internal_admin_role_event.send(sender=self.__class__, user_id=self.user_id, action=ROLE_ACTIONS.REVOKE)


class InternalAdminRoleManager(object):
    """
    This class encapsulates various operations involved in keeping Internal Admin access rights
    """
    _logger = logging.getLogger(__name__)

    _role_actions_map = {
        ROLE_ACTIONS.GRANT: user_api.add_user_role,
        ROLE_ACTIONS.REVOKE: user_api.delete_user_role
    }

    _course_operations_map = {
        ASSOCIATION_ACTIONS.ADD: user_api.add_user_role,
        ASSOCIATION_ACTIONS.REMOVE: user_api.delete_user_role
    }

    _program_operations_map = {
        ASSOCIATION_ACTIONS.ADD: user_api.add_user_role,
        ASSOCIATION_ACTIONS.REMOVE: user_api.delete_user_role
    }

    @staticmethod
    def get_all_internal_admins():
        internal_admins_group_id = next(
            group.id
            for group in group_api.get_groups_of_type(PERMISSION_TYPE)
            if group.name == PERMISSION_GROUPS.INTERNAL_ADMIN
        )
        return set(user.id for user in group_api.get_users_in_group(internal_admins_group_id))

    @classmethod
    def _get_internal_admins_in_organization(cls, organization):
        return cls.get_all_internal_admins() & set(student.id for student in organization.fetch_students())

    @classmethod
    def handle_internal_admin_role_event(cls, sender, *args, **kwargs):
        user_id, action = kwargs.get('user_id'), kwargs.get('action')
        if action not in cls._role_actions_map:
            cls._logger.info("Unknown role action %s - skipping", action)

        organizations = user_api.get_user_organizations(user_id, organization_object=Client)
        course_ids = set()
        for org in organizations:
            for program in org.fetch_programs():
                program_courses = program.fetch_courses()
                course_ids |= set(course.course_id for course in program_courses)

        operation = cls._role_actions_map[action]

        cls._do_role_management(operation, [user_id], course_ids, USER_ROLES.INTERNAL_ADMIN)

    @classmethod
    def handle_course_program_event(cls, sender, *args, **kwargs):
        course_id, program_id, action = kwargs.get('course_id'), kwargs.get('program_id'), kwargs.get('action')
        organizations = group_api.get_organizations_in_group(program_id, group_object=Client)

        user_ids = set()
        for org in organizations:
            user_ids |= cls._get_internal_admins_in_organization(org)

        operation = cls._course_operations_map[action]

        cls._do_role_management(operation, user_ids, [course_id], USER_ROLES.INSTRUCTOR)

    @classmethod
    def handle_program_client_event(cls, sender, *args, **kwargs):
        client_id, program_id, action = kwargs.get('client_id'), kwargs.get('program_id'), kwargs.get('action')
        organization = organization_api.fetch_organization(client_id, organization_object=Client)

        user_ids = cls._get_internal_admins_in_organization(organization)
        course_ids = set(course.course_id for course in group_api.get_courses_in_group(program_id))

        operation = cls._program_operations_map[action]

        cls._do_role_management(operation, user_ids, course_ids, USER_ROLES.INSTRUCTOR)

    @classmethod
    def _do_role_management(cls, operation, users, courses, role):
        for course_id in courses:
            for user_id in users:
                operation(user_id, course_id, role)

internal_admin_role_event.connect(InternalAdminRoleManager.handle_internal_admin_role_event)
course_program_event.connect(InternalAdminRoleManager.handle_course_program_event)
program_client_event.connect(InternalAdminRoleManager.handle_program_client_event)
