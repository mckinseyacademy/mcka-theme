import copy
import logging
import time
from admin.models import (
    internal_admin_role_event, course_program_event, program_client_event, Client,
    ROLE_ACTIONS, ASSOCIATION_ACTIONS, internal_course_event, new_internal_admin_event
)
from django.core.cache import cache
from api_client import user_api, group_api, course_api, organization_api
from api_client.user_api import USER_ROLES
from api_client.group_api import PERMISSION_GROUPS, PERMISSION_TYPE
from api_client.api_error import ApiError
from django.conf import settings

from api_client.group_api import TAG_GROUPS


# map of role granting rights according to user type
ROLE_GRANT_RIGHTS = {
    PERMISSION_GROUPS.MCKA_ADMIN: [
        PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN,
        PERMISSION_GROUPS.MCKA_SUBADMIN, PERMISSION_GROUPS.COMPANY_ADMIN
    ],
    PERMISSION_GROUPS.MCKA_SUBADMIN: [
        PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_SUBADMIN, PERMISSION_GROUPS.COMPANY_ADMIN
    ],
    PERMISSION_GROUPS.INTERNAL_ADMIN: [PERMISSION_GROUPS.INTERNAL_ADMIN]
}


class PermissionSaveError(Exception):
    pass


class Permissions(object):

    ''' Handles loading and saving user permissions and roles '''

    permission_for_role = {
        USER_ROLES.TA: PERMISSION_GROUPS.MCKA_TA,
        USER_ROLES.OBSERVER: PERMISSION_GROUPS.MCKA_OBSERVER
    }
    CACHE_EXPIRE_TIME = 300 # every five minutes it will refresh courses list
    def __init__(self, user_id, ):
        self.permission_groups = self.get_groups_of_type_permission_cached()
        self.current_permissions = [pg.name for pg in user_api.get_user_groups(user_id, PERMISSION_TYPE)]
        self.courses = self.get_course_list_or_cached()
        self.user_roles = user_api.get_user_roles(user_id)
        self.user_id = user_id

    def get_course_list_or_cached(self, force_fetch = False):
        course_list = cache.get('course_list_cached', None)
        time_now = time.time()
        if course_list is None or force_fetch:
            course_list = course_api.get_course_list()
            cache.set('course_list_cached', course_list)
            time_now = time.time()
            cache.set('course_list_cached_last_update_time', time_now)
        else:
            course_list_last_update_time = cache.get('course_list_cached_last_update_time', None)
            if course_list_last_update_time:
                if time_now - course_list_last_update_time > self.CACHE_EXPIRE_TIME:
                    course_list = course_api.get_course_list()
                    cache.set('course_list_cached', course_list)
                    cache.set('course_list_cached_last_update_time', time_now)
            else:
                cache.set('course_list_cached_last_update_time', time_now)
        return course_list
    
    def get_groups_of_type_permission_cached(self):
        ''' Loads and caches group names and ids via the edX platform '''
        permission_groups = cache.get('permission_groups_cached', None)
        if permission_groups is None:
            permission_groups = group_api.get_groups_of_type(PERMISSION_TYPE)
            cache.set('permission_groups_cached', permission_groups)

        return permission_groups

    def add_course_role(self, course_id, role):
        per_course_roles = [{"course_id": p.course_id, "role": p.role}
                            for p in self.user_roles if p.course_id != course_id and p.role != role]
        per_course_roles.append({
            "course_id": course_id,
            "role": role,
        })
        self.save(copy.copy(self.current_permissions), per_course_roles)

    def remove_all_course_roles(self, course_id):
        per_course_roles = [{"course_id": p.course_id, "role": p.role}
                            for p in self.user_roles if p.course_id != course_id]
        new_perms = [
                    perm for perm in self.current_permissions
                    if perm not in (PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.MCKA_OBSERVER)
                ]
        self.save(new_perms, per_course_roles)

    def update_course_role(self, course_id, role):
        per_course_roles = []
        current_course_roles = {}
        for p in self.user_roles:
            if p.course_id == course_id:
                current_course_roles = {"course_id": p.course_id, "role": p.role}
            else:
                per_course_roles.append({"course_id": p.course_id, "role": p.role})
        if current_course_roles.get("role", None) == role:
            return
        elif role in self.permission_for_role.keys():
            per_course_roles.append({
                "course_id": course_id,
                "role": role,
            })
        new_perms = [
                    perm for perm in self.current_permissions
                    if perm not in (PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.MCKA_OBSERVER)
                ]
        self.save(new_perms, per_course_roles)

    def update_courses_roles_list(self, courses_roles_list):
        per_course_roles = [{"course_id": p.course_id, "role": p.role}
                            for p in self.user_roles if p.course_id != course_id]

        for course_role in courses_roles_list:
            per_course_roles.append({
                "course_id": course_role['course_id'],
                "role": course_role['role'],
            })
        new_perms = [
                    perm for perm in self.current_permissions
                    if perm not in (PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.MCKA_OBSERVER)
                ]
        self.save(new_perms, per_course_roles)

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
            if permission_name == PERMISSION_GROUPS.INTERNAL_ADMIN:
                # internal_admin_role_event.send(sender=self.__class__, user_id=self.user_id, action=ROLE_ACTIONS.GRANT)
                new_internal_admin_event.send(sender=self.__class__, user_id=self.user_id, action=ROLE_ACTIONS.GRANT)

    def remove_permission(self, permission_name):
        group_id = self.get_group_id(permission_name)
        if group_id:
            group_api.remove_user_from_group(self.user_id, group_id)
            if permission_name == PERMISSION_GROUPS.INTERNAL_ADMIN:
                # internal_admin_role_event.send(sender=self.__class__, user_id=self.user_id, action=ROLE_ACTIONS.REVOKE)
                new_internal_admin_event.send(sender=self.__class__, user_id=self.user_id, action=ROLE_ACTIONS.REVOKE)
    
    def add_company_admin_permissions(self, organization_ids):
        group_id = self.get_group_id(PERMISSION_GROUPS.COMPANY_ADMIN)
        if group_id:
            user_organizations_data = self.get_all_user_organizations_with_permissions()
            first_pass = True
            for organization_id in organization_ids:

                all_organization_groups = organization_api.get_all_organization_groups(organization_id)

                add_company_admin_group = True
                for organization_group in all_organization_groups:
                    if organization_group["type"] == PERMISSION_TYPE and int(group_id) == int(organization_group["id"]):
                        add_company_admin_group = False 
                        break
                if add_company_admin_group:
                    organization_api.add_group_to_organization(organization_id, group_id)

                if int(organization_id) not in user_organizations_data["company_ids"]:
                    organization_api.add_user_to_organization(organization_id, self.user_id)

                if PERMISSION_GROUPS.COMPANY_ADMIN not in self.current_permissions and first_pass:
                    group_api.add_user_to_group(self.user_id, group_id)
                    first_pass = False

                add_user_to_company_admin = True
                for organization in user_organizations_data[PERMISSION_GROUPS.COMPANY_ADMIN]:
                    if int(organization_id) == int(organization.id):
                        add_user_to_company_admin = False
                if add_user_to_company_admin:
                    organization_api.add_users_to_organization_group(organization_id, group_id, self.user_id)

    def remove_company_admin_permission(self, organization_ids):
        group_id = self.get_group_id(PERMISSION_GROUPS.COMPANY_ADMIN)
        if group_id:
            user_organizations = self.get_all_user_organizations_with_permissions()
            for organization_id in organization_ids:
                if user_organizations["company_num"] > 1:
                    organization_api.remove_users_from_organization(organization_id, self.user_id)
                    user_organizations["company_num"] -= 1

                remove_global_company_admin = True
                if len(user_organizations[PERMISSION_GROUPS.COMPANY_ADMIN]) > 1:
                    remove_global_company_admin = False
                    
                if remove_global_company_admin:
                    group_api.remove_user_from_group(self.user_id, group_id)
                organization_api.remove_users_from_organization_group(organization_id, group_id, self.user_id)
                user_organizations[PERMISSION_GROUPS.COMPANY_ADMIN] = [organization for organization in user_organizations[PERMISSION_GROUPS.COMPANY_ADMIN] 
                                                                        if int(organization_id) != int(organization.id)]
                                                                        
    def update_company_admin_permissions(self, organization_ids):
        group_id = self.get_group_id(PERMISSION_GROUPS.COMPANY_ADMIN)
        if group_id:
            list_to_remove = []
            list_to_add = []
            list_of_current_permissions = []
            user_organizations = self.get_all_user_organizations_with_permissions()

            for organization in user_organizations[PERMISSION_GROUPS.COMPANY_ADMIN]:
                list_of_current_permissions.append(organization.id)
                if organization.id not in organization_ids:
                    list_to_remove.append(organization.id)

            for organization_id in organization_ids:
                if organization_id not in list_of_current_permissions:
                    list_to_add.append(organization_id)

            if len(list_to_add):
                self.add_company_admin_permissions(list_to_add)
            if len(list_to_remove):
                self.remove_company_admin_permission(list_to_remove)

    def check_if_company_admin(self, organization_id, group_id = None):
        if not group_id:
            group_id = self.get_group_id(PERMISSION_GROUPS.COMPANY_ADMIN)
        if group_id:
            company_admin_list = organization_api.get_users_from_organization_group(organization_id, group_id)
            for company_admin in company_admin_list:
                if int(company_admin["id"]) == int(self.user_id):
                    return True
            return False
        else:
            return False

    def get_all_user_organizations_with_permissions(self):
        group_id = self.get_group_id(PERMISSION_GROUPS.COMPANY_ADMIN)
        user_statuses = {PERMISSION_GROUPS.COMPANY_ADMIN:[], "main_company":[], "company_num":0}
        if group_id:
            organizations_list = user_api.get_user_organizations(self.user_id)
            user_statuses["company_num"] = len(organizations_list)
            user_statuses["company_ids"] = []
            for organization in organizations_list:
                user_statuses["company_ids"].append(int(organization.id))
                if self.check_if_company_admin(organization.id, group_id):
                    user_statuses[PERMISSION_GROUPS.COMPANY_ADMIN].append(organization)
                else:
                    user_statuses["main_company"].append(organization)
            if user_statuses["company_num"] > 0 and len(user_statuses["main_company"]) == 0: #naive approach that main company is first company
                user_statuses["main_company"].append(user_statuses[PERMISSION_GROUPS.COMPANY_ADMIN][0])
        else:
            organizations_list = user_api.get_user_organizations(self.user_id)
            user_statuses["company_num"] = 1
            user_statuses["company_ids"] = []
            if len(organizations_list) > 0:
                user_statuses["main_company"].append(organizations_list[0])
                user_statuses["company_ids"].append(int(organizations_list[0].id))
        return user_statuses

    def has_grant_rights(self, role_to_grant):
        """
        Checks whether a user can grant access for a particular role

        Args:
            role_to_grant (str): name of the role
        """

        # user types which can assign this role
        can_assign_roles = [
            role
            for role, groups in ROLE_GRANT_RIGHTS.items()
            if role_to_grant in groups
        ]

        if set(self.current_permissions).intersection(can_assign_roles):
            return True

        return False


class SlimAddingPermissions(object):
    
    permission_for_role = {
        USER_ROLES.TA: PERMISSION_GROUPS.MCKA_TA,
        USER_ROLES.OBSERVER: PERMISSION_GROUPS.MCKA_OBSERVER
    }

    def __init__(self, user_id, ):
        self.permission_groups = self.get_groups_of_type_permission_cached()
        self.user_id = user_id

    def get_groups_of_type_permission_cached(self):
        ''' Loads and caches group names and ids via the edX platform '''
        permission_groups = cache.get('permission_groups_cached', None)
        if permission_groups is None:
            permission_groups = group_api.get_groups_of_type(PERMISSION_TYPE)
            cache.set('permission_groups_cached', permission_groups)

        return permission_groups

    def add_course_role(self, course_id, role):
        per_course_roles = []
        per_course_roles.append({
            "course_id": course_id,
            "role": role,
        })

        user_api.update_user_roles(self.user_id, {'roles': per_course_roles, 'ignore_roles': settings.IGNORE_ROLES})
        self.add_permission(self.permission_for_role.get(role, ""))

    def get_group_id(self, permission_name):
        return next((g.id for g in self.permission_groups if g.name == permission_name), None)

    def add_permission(self, permission_name):
        group_id = self.get_group_id(permission_name)
        if group_id:
            group_api.add_user_to_group(self.user_id, group_id)


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
    def _get_all_internal_courses(cls):

        internal_ids = []
        internal_tags = group_api.get_groups_of_type(group_type=TAG_GROUPS.INTERNAL)
        internal_courses = []
        for internal_tag in internal_tags:
            internal_courses.extend(group_api.get_courses_in_group(group_id=internal_tag.id))
        for course in internal_courses:
            internal_ids.append(course.course_id)

        return set(internal_ids)

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

        cls._do_role_management(operation, [user_id], course_ids, USER_ROLES.INSTRUCTOR)

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
    def handle_internal_course_event(cls, sender, *args, **kwargs):
        course_id, action = kwargs.get('course_id'), kwargs.get('action')

        user_ids = cls.get_all_internal_admins()

        operation = cls._course_operations_map[action]

        cls._do_role_management(operation, user_ids, [course_id], USER_ROLES.INSTRUCTOR)

    @classmethod
    def handle_new_internal_admin_event(cls, sender, *args, **kwargs):
        user_id, action = kwargs.get('user_id'), kwargs.get('action')

        course_ids = cls._get_all_internal_courses()

        operation = cls._role_actions_map[action]

        cls._do_role_management(operation, [user_id], course_ids, USER_ROLES.INSTRUCTOR)

    @classmethod
    def _do_role_management(cls, operation, users, courses, role):
        for course_id in courses:
            for user_id in users:
                operation(user_id, course_id, role)

internal_admin_role_event.connect(InternalAdminRoleManager.handle_internal_admin_role_event)
course_program_event.connect(InternalAdminRoleManager.handle_course_program_event)
program_client_event.connect(InternalAdminRoleManager.handle_program_client_event)
internal_course_event.connect(InternalAdminRoleManager.handle_internal_course_event)
new_internal_admin_event.connect(InternalAdminRoleManager.handle_new_internal_admin_event)
