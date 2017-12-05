from __future__ import division
import functools
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from accounts.middleware.thread_local import get_static_tab_context
from admin.controller import load_course
from admin.models import Program, ClientNavLinks, ClientCustomization, BrandingSettings, LearnerDashboard
from api_client import user_api, course_api
from license import controller as license_controller
from courses.models import FeatureFlags

from .controller import build_page_info_for_course, locate_chapter_page, load_static_tabs, load_lesson_estimated_time, round_to_int

CURRENT_COURSE_ID = "current_course_id"
CURRENT_PROGRAM_ID = "current_program_id"
CURRENT_PROGRAM = "current_program"

def _load_intersecting_program_courses(program, courses):
    if program.id == Program.NO_PROGRAM_ID:
        program.courses = courses
        program.outside_courses = None
    else:
        program_course_ids = [course.course_id for course in program.fetch_courses()]
        program.courses = [course for course in courses if course.id in program_course_ids]
        program.outside_courses = [course for course in courses if course.id not in program_course_ids]

def get_current_course_by_user_id(user_id):
    # Return first active course in the user's list
    courses = user_api.get_user_courses(user_id)
    courses = [c for c in courses if c.is_active and c.started]
    if len(courses) > 0:
        course_id = courses[0].id
        return course_id
    return None

def get_current_course_for_user(request):
    course_id = request.session.get(CURRENT_COURSE_ID, None)

    if not course_id and request.user:
        course_id = user_api.get_user_preferences(request.user.id).get(CURRENT_COURSE_ID, None)

    if not course_id and request.user:
        course_id = get_current_course_by_user_id(request.user.id)

    return course_id


def set_current_program_for_user(request, program, update_api=True):
    prev_program = request.session.get(CURRENT_PROGRAM, None)
    if prev_program is None or (prev_program.id != program.id):
        request.session[CURRENT_PROGRAM] = program
        request.session[CURRENT_PROGRAM_ID] = program.id

        if update_api:
            user_api.set_user_preferences(
                request.user.id,
                {
                    CURRENT_PROGRAM_ID: str(program.id),
                }
            )

def set_current_course_for_user(request, course_id):
    prev_course_id = request.session.get(CURRENT_COURSE_ID, None)
    if prev_course_id != course_id:
        request.session[CURRENT_COURSE_ID] = course_id

        # Additionally set the current program for this user
        current_program = None
        courses = user_api.get_user_courses(request.user.id)
        for program in Program.user_programs_with_course(request.user.id, course_id):
            if license_controller.fetch_granted_license(program.id, request.user.id) is not None:
                current_program = program
                break

        if current_program is None:
            # Fake program
            current_program = Program.no_program()

        user_api.set_user_preferences(
            request.user.id,
            {
                CURRENT_COURSE_ID: course_id,
                CURRENT_PROGRAM_ID: str(current_program.id),
            }
        )

        _load_intersecting_program_courses(current_program, courses)
        set_current_program_for_user(request, current_program, update_api=False)

def clear_current_course_for_user(request):
    request.session[CURRENT_COURSE_ID] = None
    user_api.delete_user_preference(request.user.id, CURRENT_COURSE_ID)

def get_current_program_for_user(request):

    # Attempt to load from current session
    program = request.session.get(CURRENT_PROGRAM, None)

    # Attempt to load from user preferences
    if not program and request.user:
        program_id = user_api.get_user_preferences(request.user.id).get(CURRENT_PROGRAM_ID, None)
        if program_id == Program.NO_PROGRAM_ID:
            program = Program.no_program()
        elif program_id:
            program = Program.fetch(program_id)

        # if not attempt to load first program
        if not program:
            current_course_id = get_current_course_for_user(request)
            programs = []
            if current_course_id:
                programs = Program.user_programs_with_course(
                    request.user.id,
                    current_course_id,
                )
            else:
                programs = Program.user_program_list(request.user.id)
            if len(programs) > 0:
                program = Program.fetch(programs[0].id)

            # if user goes to LD after the first login (without accessing any course)
            if not program:
                program = Program.no_program()

        if program:
            _load_intersecting_program_courses(program, user_api.get_user_courses(request.user.id))
            set_current_program_for_user(request, program, update_api=False)

    # Return the program to the caller
    return program

class CourseAccessDeniedError(PermissionDenied):
    '''
    Exception to be thrown when course access is denied
    '''
    def __init__(self, course_id, user_id):
        self.course_id = course_id
        self.user_id = user_id
        super(CourseAccessDeniedError, self).__init__()

    def __str__(self):
        return "Access denied to course '{}' for user {}".format(self.course_id, self.user_id)

    def __unicode__(self):
        return u"Access denied to course '{}' for user {}".format(self.course_id, self.user_id)

def check_user_course_access(func):
    '''
    Decorator which will raise an CourseAccessDeniedError if the user does not have access to the requested course
    '''
    @functools.wraps(func)
    def user_course_access_checker(request, course_id, *args, **kwargs):
        try:
            program = get_current_program_for_user(request)
            if program is None:
                set_current_course_for_user(request, course_id)
                program = get_current_program_for_user(request)
                if program is None:
                    raise CourseAccessDeniedError(course_id, request.user.id)
            course_access = [c for c in program.courses if c.id == course_id]
            if len(course_access) < 1 and program.outside_courses and len(program.outside_courses) > 0:
                course_access = [c for c in program.outside_courses if c.id == course_id]
            if len(course_access) < 1:
                raise CourseAccessDeniedError(course_id, request.user.id)
            # Finally, even if they've got access - if not started redirect to notready page
            if not course_access[0].started:
                return HttpResponseRedirect('/courses/{}/notready'.format(course_id))
        except CourseAccessDeniedError:
            # they've tried to go elsewhere, so let's not even worry about holding
            # onto the last course visited, trash it so a visit to homepage after
            # getting this error will do the right thing and rebuild a correct list
            # in case this was a course for which they previously had access, but now don't
            clear_current_course_for_user(request)
            # re-raise this error
            raise

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
        return "Access denied to user {} for data belonging to {}".format(self.admin_user_id, self.user_id)

    def __unicode__(self):
        return u"Access denied to user {} for data belonging to {}".format(self.admin_user_id, self.user_id)

def check_company_admin_user_access(func):
    '''
    Decorator which will raise a CompanyAdminAccessDeniedError if user and company admin user do not have a common organization
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

def _get_course_progress_data(course, user_id):
    completions = course_api.get_course_completions(course.id, user_id)
    completed_ids = [result.content_id for result in completions]
    component_ids = course.components_ids(settings.PROGRESS_IGNORE_COMPONENTS)
    for lesson in course.chapters:
        lesson.progress = 0
        lesson_component_ids = course.lesson_component_ids(lesson.id, completed_ids,
                                                           settings.PROGRESS_IGNORE_COMPONENTS)
        if len(lesson_component_ids) > 0:
            matches = set(lesson_component_ids).intersection(completed_ids)
            lesson.progress = round_to_int(100 * len(matches) / len(lesson_component_ids))
    actual_completions = set(component_ids).intersection(completed_ids)
    return len(actual_completions), len(component_ids)

def load_course_progress(course, user_id):
    actual_completions_len, component_ids_len = _get_course_progress_data(course, user_id)
    try:
        course.user_progress = round_to_int(100 * actual_completions_len / component_ids_len)
    except ZeroDivisionError:
        course.user_progress = 0


def return_course_completions_stats(course, user_id):
    return _get_course_progress_data(course, user_id)


STANDARD_DATA_FEATURES = {
    "course_progress": True,
}


def standard_data(request):
    features_to_include = getattr(request, 'standard_data_features', STANDARD_DATA_FEATURES)

    ''' Makes user and program info available to all templates '''
    course = None
    program = None
    upcoming_course = None
    client_nav_links = None
    client_customization = None
    branding = None
    feature_flags = None
    learner_dashboard_flag = False
    discover_flag = False
    programs = None
    organization_id = None

    # have we already fetched this before and attached it to the current request?
    if hasattr(request, 'user_program_data'):
        return request.user_program_data

    if request.user and request.user.id:
        # test loading the course to see if we can; if not, we destroy cached
        # information about current course and let the new course_id load again
        # in subsequent calls
        try:
            course_id = get_current_course_for_user(request)
            if course_id is not None:
                course = load_course(course_id, request=request)
                if not course.started:
                    raise CourseAccessDeniedError(course_id, request.user.id)
        except:
            clear_current_course_for_user(request)
            course = None
            course_id = get_current_course_for_user(request)

        program = get_current_program_for_user(request)
        if course_id:
            try:
                feature_flags = FeatureFlags.objects.get(course_id=course_id)
                learner_dashboard_flag = feature_flags.learner_dashboard
                discover_flag = feature_flags.discover
            except:
                learner_dashboard_flag = False
                discover_flag = False

            lesson_id = request.resolver_match.kwargs.get('chapter_id', None)
            module_id = request.resolver_match.kwargs.get('page_id', None)

            if module_id is None or lesson_id is None:
                course_id, lesson_id, page_id = locate_chapter_page(
                    request, request.user.id, course_id, None)

            course = build_page_info_for_course(request, course_id, lesson_id, module_id)
            # Inject formatted data for view (don't pass page_id in here - if needed it will be processed from elsewhere)
            _inject_formatted_data(program, course, None, load_static_tabs(course_id))

            if features_to_include['course_progress']:
                # Inject course progress for nav header
                load_course_progress(course, request.user.id)

        elif program and program.courses:
            upcoming_course = program.courses[0]

        organizations = user_api.get_user_organizations(request.user.id)

        if organizations:
            organization = organizations[0]
            organization_id = organization.id
            try:
                client_customization = ClientCustomization.objects.get(client_id=organization_id)
            except ClientCustomization.DoesNotExist:
                client_customization = None

            try:
                if feature_flags and feature_flags.branding:
                    branding = BrandingSettings.objects.get(client_id=organization_id)
                else:
                    branding = None
            except:
                branding = None

            client_nav_links = ClientNavLinks.objects.filter(client_id=organization_id)
            client_nav_links = dict((link.link_name, link) for link in client_nav_links)
            
        if course:
            if course.ended:
                if len(course.name) > 37:
                    course.name = course.name[:37] + '...'
            else:
                if len(course.name) > 57:
                    course.name = course.name[:57] + '...'

            programs = get_program_menu_list(request, course)

    data = {
        "course": course,
        "program": program,
        "programs": programs,
        "upcoming_course": upcoming_course,
        "client_customization": client_customization,
        "client_nav_links": client_nav_links,
        "branding": branding,
        "learner_dashboard_flag": learner_dashboard_flag,
        "discover_flag": discover_flag,
        "organization_id": organization_id
    }

    # point to this data from the request object, just in case we re-enter this method somewhere
    # else down the execution pipeline, e.g. context_processing
    request.user_program_data = data

    return data

def get_program_menu_list(request, current_course):

    programs = []
    current_program = None
    user_programs = Program.user_program_list(request.user.id)
    user_courses = user_api.get_user_courses(request.user.id)

    for program in user_programs:

        row = []
        program_courses = []
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
        row = []
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
