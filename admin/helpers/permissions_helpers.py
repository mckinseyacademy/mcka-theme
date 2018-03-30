import functools

from rest_framework import permissions
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.template import loader, RequestContext
from django.http import HttpResponseForbidden

from api_client import user_api, organization_api
from admin.controller import (
    check_if_course_is_internal, check_if_user_is_internal, get_internal_courses_ids,
    get_ta_accessible_course_ids
)
from admin.permissions import Permissions, PERMISSION_GROUPS
from admin.models import Client


def permission_denied(request):
    template = loader.get_template('not_authorized.haml')
    context = RequestContext(request, {'request_path': request.path})
    return HttpResponseForbidden(template.render(context))


class InternalAdminCoursePermission(permissions.BasePermission):
    """
    Permission check that an internal admin can only access
    the courses tagged as `internal`

    This class should only be used for ensuring this particular case it does
    not check for any related permissions
    """
    def has_permission(self, request, view):
        """
        Implements the actual permission check
        """
        course_id = view.kwargs.get('course_id')

        return not (request.user.is_authenticated() and
                    request.user.is_internal_admin and not check_if_course_is_internal(course_id))


class InternalAdminUserPermission(permissions.BasePermission):
    """
    Permission check that an internal admin can only perform
    action on a user which is enrolled in an `internal` course

    This class should only be used for ensuring this particular case it does
    not check for any related permissions
    """
    def has_permission(self, request, view):
        """
        Implements the actual permission check
        """
        user_id = view.kwargs.get('user_id')

        return not (request.user.is_authenticated() and
                    request.user.is_internal_admin and not check_if_user_is_internal(user_id))


class CompanyAdminCompanyPermission(permissions.BasePermission):
    """
    Permission check that a company admin can only access
    a company for which it has company-admin rights

    This class should only be used for ensuring this particular case it does
    not check for any related permissions
    """
    def has_permission(self, request, view):
        """
        Implements the actual permission check
        """
        company_id = int(view.kwargs.get('company_id'))

        user_organization_permissions = Permissions(request.user.id).get_all_user_organizations_with_permissions()
        user_administrated_organizations = user_organization_permissions.get(PERMISSION_GROUPS.COMPANY_ADMIN, [])

        is_current_company_admin = company_id in [user_org.id for user_org in user_administrated_organizations]
        unauthorized_user = request.user.is_authenticated() and request.user.is_company_admin and\
            not is_current_company_admin

        return not unauthorized_user


class CompanyAdminUserPermission(permissions.BasePermission):
    """
    Permission check that a company admin is performing action
    on a user who belongs to its companies

    This class should only be used for ensuring this particular case it does
    not check for any related permissions
    """
    def has_permission(self, request, view):
        """
        Implements the actual permission check
        """
        user_id = view.kwargs.get('user_id')
        company_id = view.kwargs.get('company_id')

        if not request.user.is_authenticated() or not request.user.is_company_admin:
            return True

        if company_id:
            return not (
                request.user.is_authenticated() and int(company_id)
                not in [user_org.id for user_org in user_api.get_user_organizations(user_id)]
            )
        else:
            user_organizations = [user_org.id for user_org in user_api.get_user_organizations(user_id)]
            admin_organizations = [
                user_org.id
                for user_org in Permissions(request.user.id).get_all_user_organizations_with_permissions()
                    .get(PERMISSION_GROUPS.COMPANY_ADMIN, [])
            ]

            return set(user_organizations).intersection(admin_organizations)


class CompanyAdminCoursePermission(permissions.BasePermission):
    """
    Permission check that a company admin is performing action
    on a course who belongs to its companies

    This class should only be used for ensuring this particular case it does
    not check for any related permissions
    """
    def has_permission(self, request, view):
        """
        Implements the actual permission check
        """
        course_id = view.kwargs.get('course_id')
        company_id = request.GET.get('company_id', None)

        if request.user.is_company_admin:
            if not company_id or int(company_id) not in [
                user_org.id
                for user_org in Permissions(request.user.id).get_all_user_organizations_with_permissions()
                        .get(PERMISSION_GROUPS.COMPANY_ADMIN, [])
            ]:
                return False

            company_courses = organization_api.get_organizations_courses(company_id)

            if course_id not in [course.get('id') for course in company_courses]:
                return False

        return True


class AccessChecker(object):
    @staticmethod
    def get_organization_for_user(user):
        try:
            return user_api.get_user_organizations(user.id, parse_object=Client)[0]
        except IndexError:
            return None

    @staticmethod
    def get_clients_user_has_access_to(user):
        if user.is_mcka_admin or user.is_mcka_subadmin:
            return Client.list()
        return user_api.get_user_organizations(user.id, parse_object=Client)

    @staticmethod
    def get_courses_for_organization(org):
        courses = []
        for program in org.fetch_programs():
            courses.extend(program.fetch_courses())

        return set(course.course_id for course in courses)

    @staticmethod
    def _do_wrapping(func, request, restrict_to_key, restrict_to_callback, *args, **kwargs):
        restrict_to_ids = []
        if request.user.is_mcka_admin or request.user.is_mcka_subadmin:
            restrict_to_ids = None
        else:
            org = AccessChecker.get_organization_for_user(request.user)
            if org:
                restrict_to_ids = restrict_to_callback(org)

        kwargs[restrict_to_key] = restrict_to_ids

        try:
            return func(request, *args, **kwargs)
        except PermissionDenied:
            return permission_denied(request)

    @staticmethod
    def check_has_course_access(course_id, restrict_to_courses_ids):
        if restrict_to_courses_ids is not None and course_id not in restrict_to_courses_ids:
            raise PermissionDenied()

    @staticmethod
    def check_has_program_access(program_id, restrict_to_programs_ids):
        if restrict_to_programs_ids is not None and program_id not in restrict_to_programs_ids:
            raise PermissionDenied()

    @staticmethod
    def check_has_user_access(student_id, restrict_to_users_ids):
        if restrict_to_users_ids is not None and student_id not in restrict_to_users_ids:
            raise PermissionDenied()

    @staticmethod
    def program_access_wrapper(func):
        """
        Ensure restricted roles (company admin, internal admin, ta)
        can only access programs mapped to their companies.

        Note it changes function signature, passing additional parameter restrict_to_programs_ids. Due to the fact it would
        make a huge list of programs for mcka admin, if user is mcka admin restrict_to_programs_ids is None
        """
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            restrict_to_callback = lambda org: set(program.id for program in org.fetch_programs())
            return AccessChecker._do_wrapping(
                func, request, 'restrict_to_programs_ids', restrict_to_callback, *args, **kwargs
            )

        return wrapper

    @staticmethod
    def course_access_wrapper(func):
        """
        Ensure restricted roles (company admin, internal admin, ta)
        can only access courses mapped to their companies.

        Note it changes function signature, passing additional parameter restrict_to_courses_ids. Due to the fact it
        would make a huge list of courses for mcka admin, if user is mcka admin restrict_to_courses_ids is None
        """
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            restrict_to_callback = AccessChecker.get_courses_for_organization
            return AccessChecker._do_wrapping(
                func, request, 'restrict_to_courses_ids', restrict_to_callback, *args, **kwargs
            )

        return wrapper

    @staticmethod
    def users_access_wrapper(func):
        """
        Ensure restricted roles (company admin, internal admin, ta)
        can only access users in their companies.

        Note it changes function signature, passing additional parameter allowed_user_ids. Due to the fact it would
        make a huge list of users for mcka admin, if user is mcka admin restrict_to_users_ids is None
        """
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            restrict_to_callback = lambda org: set(user_id for user_id in org.users)
            return AccessChecker._do_wrapping(
                func, request, 'restrict_to_users_ids', restrict_to_callback, *args, **kwargs
            )

        return wrapper

    @staticmethod
    def internal_admin_user_access_wrapper(func):
        """
        Ensure internal admin can only access users
        which are enrolled in `internal` tagged courses
        """
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            user_id = kwargs.get('user_id')
            if request.user.is_internal_admin and user_id and not check_if_user_is_internal(user_id):
                return permission_denied(request)
            else:
                return func(request, *args, **kwargs)

        return wrapper

    @staticmethod
    def internal_admin_course_access_wrapper(func):
        """
        Ensure internal admin can only access `internal` courses
        """
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            course_id = kwargs.get('course_id')
            if request.user.is_internal_admin and course_id and course_id not in get_internal_courses_ids():
                return permission_denied(request)
            else:
                return func(request, *args, **kwargs)

        return wrapper


    @staticmethod
    def company_admin_user_access_wrapper(func):
        """
        Ensure company admin can only access users in their organizations
        """
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            user_id = kwargs.get('user_id')

            if request.user.is_company_admin and user_id:
                user_organizations = [user_org.id for user_org in user_api.get_user_organizations(user_id)]
                admin_organizations = [
                    user_org.id
                    for user_org in Permissions(request.user.id).get_all_user_organizations_with_permissions()
                    .get(PERMISSION_GROUPS.COMPANY_ADMIN, [])
                ]

                if not set(user_organizations).intersection(admin_organizations):
                    return permission_denied(request)

            return func(request, *args, **kwargs)

        return wrapper

    @staticmethod
    def company_admin_company_access_wrapper(func):
        """
        Ensure company admin can only access their companies
        """
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            company_id = kwargs.get('company_id')
            if request.user.is_company_admin and int(company_id) not in [
                user_org.id
                for user_org in Permissions(request.user.id).get_all_user_organizations_with_permissions()
                        .get(PERMISSION_GROUPS.COMPANY_ADMIN, [])
            ]:
                return permission_denied(request)

            return func(request, *args, **kwargs)

        return wrapper

    @staticmethod
    def ta_course_access_wrapper(func):
        """
        Ensure TA user can only access TA accessible courses
        """
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            course_id = kwargs.get('course_id')
            user = request.user

            # ensure TA user can only access an assigned course
            if not any([user.is_client_admin, user.is_mcka_admin, user.is_internal_admin, user.is_mcka_subadmin]) \
                    and course_id not in get_ta_accessible_course_ids(user):
                raise PermissionDenied()

            return func(request, *args, **kwargs)

        return wrapper

    @staticmethod
    def client_admin_wrapper(func):
        """
        Ensure company admins can view only their company.
        MCKA Admin can view all clients in the system.
        """
        @functools.wraps(func)
        def wrapper(request, client_id=None, *args, **kwargs):
            valid_client_id = None
            if request.user.is_mcka_admin or request.user.is_mcka_subadmin:
                valid_client_id = client_id

            # make sure client admin can access only his company
            elif request.user.is_client_admin or request.user.is_internal_admin:
                org = AccessChecker.get_organization_for_user(request.user)
                if org:
                    valid_client_id = org.id

            if valid_client_id is None:
                raise Http404

            return func(request, valid_client_id, *args, **kwargs)

        return wrapper

checked_course_access = AccessChecker.course_access_wrapper
checked_user_access = AccessChecker.users_access_wrapper
checked_program_access = AccessChecker.program_access_wrapper
client_admin_access = AccessChecker.client_admin_wrapper
internal_admin_user_access = AccessChecker.internal_admin_user_access_wrapper
internal_admin_course_access = AccessChecker.internal_admin_course_access_wrapper
company_admin_user_access = AccessChecker.company_admin_user_access_wrapper
company_admin_company_access = AccessChecker.company_admin_company_access_wrapper
ta_course_access = AccessChecker.ta_course_access_wrapper
