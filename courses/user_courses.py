from __future__ import division

import functools
import pytz

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _


from accounts.json_backend import JsonBackend
from api_data_manager.organization_data import OrgDataManager
from api_data_manager.common_data import CommonDataManager, COMMON_DATA_PROPERTIES
from api_data_manager.course_data import CourseDataManager
from admin.models import Program
from admin.controller import load_course
from datetime import datetime, timedelta
from api_client import user_api, course_api, mobileapp_api, organization_api
from accounts.middleware import thread_local
from api_data_manager.user_data import UserDataManager
from .controller import (
    load_static_tabs, get_completion_percentage_from_id,
    set_user_course_progress,
    user_learner_dashboards)

CURRENT_COURSE_ID = "current_course_id"
CURRENT_PROGRAM_ID = "current_program_id"
CURRENT_PROGRAM = "current_program"
CURRENT_LD_COURSE_ID = "current_ld_course"


def set_current_course_for_user(request, course_id, course_landing_page_flag=False):
    """
    Sets current course and program for the user in backend
    """
    if not course_landing_page_flag:
        user_data = thread_local.get_basic_user_data(request.user.id)
        if hasattr(user_data.current_course, 'id') and user_data.current_course.id == course_id:
            return
    common_data_manager = CommonDataManager()

    # get program for this course
    user_programs = Program.user_program_list(request.user.id)
    program_courses_mapping = common_data_manager.get_cached_data(COMMON_DATA_PROPERTIES.PROGRAM_COURSES_MAPPING)
    current_program = Program.no_program()

    if program_courses_mapping is not None:
        for program in user_programs:
            for program_course in program_courses_mapping.get(program.id, {}).get('courses', []):
                if course_id == program_course.course_id:
                    current_program = program
                    break
    else:
        for program in Program.user_programs_with_course(request.user.id, course_id):
                current_program = program
                break

    # persist user choice
    user_api.set_user_preferences(
        request.user.id, {
            CURRENT_COURSE_ID: course_id,
            CURRENT_PROGRAM_ID: str(current_program.id),
        }
    )


def clear_current_course_for_user(request):
    user_api.delete_user_preference(request.user.id, CURRENT_COURSE_ID)


class CourseAccessDeniedError(PermissionDenied):
    '''
    Exception to be thrown when course access is denied
    '''
    def __init__(self, course_id, user_id):
        self.course_id = course_id
        self.user_id = user_id
        super(CourseAccessDeniedError, self).__init__()

    def __str__(self):
        return _("Access denied to course '{course_id}' for user {user_id}").format(
            course_id=self.course_id,
            user_id=self.user_id
        )

    def __unicode__(self):
        return _(u"Access denied to course '{course_id}' for user {user_id}").format(
            course_id=self.course_id,
            user_id=self.user_id
        )


def check_user_course_access(func):
    @functools.wraps(func)
    def user_course_access_checker(request, course_id, *args, **kwargs):
        """
        Decorator which will raise an CourseAccessDeniedError
        if the user does not have access to the requested course
        """
        raw_courses = UserDataManager(request.user.id).raw_courses
        courses = raw_courses.courses
        current_course = raw_courses.current_course
        accessible_course = None
        for course in courses:
            if course.id == course_id:
                accessible_course = course
                break

        if not accessible_course:
            # if this is set as current course then clear it
            if current_course and current_course.id == course_id:
                clear_current_course_for_user(request)

            raise CourseAccessDeniedError(course_id, request.user.id)

        if not accessible_course.started:
            return HttpResponseRedirect('/courses/{}/notready'.format(course_id))

        return func(request, course_id, *args, **kwargs)

    return user_course_access_checker


class CompanyAdminAccessDeniedError(PermissionDenied):
    '''
    Exception to be thrown when company admin has no company in common with desired user to view
    '''
    def __init__(self, user_id, admin_user_id):
        self.user_id = user_id
        self.admin_user_id = admin_user_id
        super(CompanyAdminAccessDeniedError, self).__init__()

    def __str__(self):
        return _("Access denied to user {admin_user_id} for data belonging to {user_id}").format(
            admin_user_id=self.admin_user_id,
            user_id=self.user_id
        )

    def __unicode__(self):
        return _(u"Access denied to user {admin_user_id} for data belonging to {user_id}").format(
            admin_user_id=self.admin_user_id,
            user_id=self.user_id
        )


def check_company_admin_user_access(func):
    '''
    Decorator which will raise a CompanyAdminAccessDeniedError if user and company admin user do not have a
    common organization
    '''
    @functools.wraps(func)
    def admin_user_user_access_checker(request, user_id, *args, **kwargs):
        if not request.user.is_mcka_admin and not request.user.is_mcka_subadmin:
            def org_set(uid):
                return set([o.id for o in user_api.get_user_organizations(uid)])

            common_orgs = org_set(user_id).intersection(org_set(request.user.id))
            if len(common_orgs) < 1:
                raise CompanyAdminAccessDeniedError(user_id, request.user.id)

        return func(request, user_id, *args, **kwargs)

    return admin_user_user_access_checker


def _inject_formatted_data(program, course, page_id, static_tab_info=None):
    if program:
        for program_course in program.courses:
            program_course.course_class = ""
            if program_course.id == course.id:
                program_course.course_class = "current"

    if static_tab_info:
        for idx, lesson in enumerate(course.chapters, start=1):
            lesson_description = load_static_tabs(course.id, "lesson{}".format(idx))
            if lesson_description:
                lesson.description = lesson_description.content


def load_course_progress(course, user_id=None, username=None):
    if username is None:
        username = user_api.get_user(user_id).username
    completions = course_api.get_course_completions(course.id, username)
    user_completions = completions.get(username, {})
    course.user_progress = get_completion_percentage_from_id(user_completions, 'course')
    set_user_course_progress(course, user_completions)


def standard_data(request):
    """
    Makes current_course, program and client info available to all templates
    """
    current_course = None
    program = None
    client_nav_links = None
    client_customization = None
    branding = None
    feature_flags = None
    organization_id = None
    lesson_custom_label = None
    lessons_custom_label = None
    module_custom_label = None
    modules_custom_label = None
    course = None
    learner_dashboards = None
    show_my_courses = None
    show_new_ui_tour = False

    if request.user and request.user.id:
        course_id = request.resolver_match.kwargs.get('course_id')
        if course_id:
            course = load_course(course_id, request=request, depth=0)
            feature_flags = CourseDataManager(course_id).get_feature_flags()

        user_data = thread_local.get_basic_user_data(request.user.id)
        program = user_data.current_program
        current_course = user_data.current_course
        organization = user_data.organization

        if user_data.get('new_ui_enabled'):
            show_my_courses = any(
                course for course in user_data.courses if not getattr(course, 'learner_dashboard')
            )
            learner_dashboards = user_learner_dashboards(
                request, [ld_course for ld_course in user_data.courses if getattr(ld_course, 'learner_dashboard')]
            )

        if current_course:
            course_meta_data = CourseDataManager(current_course.id).get_course_meta_data()

            if current_course.ended:
                if len(current_course.name) > 37:
                    current_course.name = current_course.name[:37] + '...'
            else:
                if len(current_course.name) > 57:
                    current_course.name = current_course.name[:57] + '...'

            if course_meta_data:
                lesson_custom_label = course_meta_data.lesson_label
                lessons_custom_label = course_meta_data.lessons_label.get('zero')
                module_custom_label = course_meta_data.module_label
                modules_custom_label = course_meta_data.modules_label.get('zero')

        if organization:
            client_data_manager = OrgDataManager(org_id=organization.id)
            organization_id = organization.id
            client_data = client_data_manager.get_org_common_data()
            client_customization = client_data.customization
            client_nav_links = client_data.nav_links

            if client_customization and client_customization.new_ui_enabled:
                remote_user = JsonBackend().get_user(request.user.id)
                new_ui_enabled_at = client_customization.new_ui_enabled_at
                margin = new_ui_enabled_at + timedelta(days=60)
                last_signin = remote_user.last_signin

                if last_signin and last_signin < new_ui_enabled_at and pytz.UTC.localize(datetime.now()) < margin:
                    show_new_ui_tour = True

            if feature_flags and feature_flags.branding:
                branding = client_data.branding

    data = {
        "current_course": current_course,
        "program": program,
        'feature_flags': feature_flags,
        'namespace': current_course.id if current_course else None,
        'course_name': current_course.name if current_course else None,
        "client_customization": client_customization,
        "client_nav_links": client_nav_links,
        "branding": branding,
        "organization_id": organization_id,
        "lesson_custom_label": lesson_custom_label,
        "module_custom_label": module_custom_label,
        "lessons_custom_label": lessons_custom_label,
        "modules_custom_label": modules_custom_label,
        "active_course": course,
        "learner_dashboards": learner_dashboards,
        "show_my_courses": show_my_courses,
        "show_new_ui_tour": show_new_ui_tour,
        "zoomed_in_lesson_navigators": "/lessons/" not in request.META.get('HTTP_REFERER', '')

    }

    return data


def get_program_menu_list(request):
    current_course, user_courses, common_data_manager = _get_user_courses(request)

    programs = []
    current_program = None
    user_programs = Program.user_program_list(request.user.id)
    program_courses_mapping = common_data_manager.get_cached_data(COMMON_DATA_PROPERTIES.PROGRAM_COURSES_MAPPING)
    for program in user_programs:
        row = []
        program_courses = []

        if program_courses_mapping is not None:
            program_data = program_courses_mapping.get(program.id, {})
            program_course_ids = [course.course_id for course in program_data.get('courses', [])]
        else:
            program_course_ids = [course.course_id for course in program.fetch_courses()]

        for program_course_id in program_course_ids:
            for i, course in enumerate(user_courses):
                if course.id == program_course_id:
                    program_courses.append(user_courses[i])
            if current_course.id == program_course_id:
                current_program = program

        row.append(program)
        row.append(program_courses)
        programs.append(row)
        user_courses = [course for course in user_courses if course not in program_courses]

    if user_courses:
        row = list()
        row.append(Program.no_program())
        row.append(user_courses)
        programs.append(row)
        if not current_program:
            current_program = Program.no_program()

    for i, program in enumerate(programs):
        if program[0] == current_program:
            if program[1]:
                move_course_to_first_place(program, current_course)
            programs.insert(0, programs.pop(i))
    return programs


def get_course_menu_list(request):
    current_course, user_courses, _ = _get_user_courses(request)
    user_courses = [u for u in user_courses if not u.ended] + [u for u in user_courses if u.ended]
    return user_courses


def _get_user_courses(request):
    common_data_manager = CommonDataManager()

    user_data = thread_local.get_basic_user_data(request.user.id)
    current_course = user_data.current_course

    companion_app_course_ids = common_data_manager.get_cached_data(COMMON_DATA_PROPERTIES.COMPANION_APP_COURSES)

    user_courses = user_data.courses
    # NEW UI: remove the user courses for which learner dashboard is enabled
    if user_data.get('new_ui_enabled'):
        user_courses = [course for course in user_courses if not getattr(course, 'learner_dashboard')]

    if companion_app_course_ids is None:
        companion_app = mobileapp_api.get_mobile_apps({"app_name": "LBG"})
        companion_app_orgs = companion_app['results'][0]['organizations'] if companion_app.get('results') else []

        companion_app_courses = []
        # get all the courses of companion app
        for org_id in companion_app_orgs:
            org_companion_app_courses = organization_api.get_organizations_courses(org_id)
            companion_app_courses.extend(org_companion_app_courses)

        # get the mobile available courses of companion app
        companion_app_course_ids = [course['id'] for course in companion_app_courses if course['mobile_available']]

        common_data_manager.set_cached_data(
            COMMON_DATA_PROPERTIES.COMPANION_APP_COURSES,
            data=companion_app_course_ids
        )

    # remove the user courses that are part of companion app
    user_courses = [course for course in user_courses if course.id not in companion_app_course_ids]
    return current_course, user_courses, common_data_manager


def move_course_to_first_place(program, current_course):
    for i, course in enumerate(program[1]):
            if course.id == current_course.id:
                program[1].insert(0, program[1].pop(i))
                program[1][0].course_class = "current"


def check_course_shell_access(request, course_id):

    access = False
    courses = user_api.get_user_courses(request.user.id)

    for course in courses:
        if course_id == course.id:
            access = True

    if not access:
        clear_current_course_for_user(request)
        request.session['last_visited_course'] = None
        raise CourseAccessDeniedError(course_id, request.user.id)
