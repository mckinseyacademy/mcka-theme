from django.conf import settings
from courses.controller import build_page_info_for_course, locate_chapter_page, load_course_progress

from courses.views import _inject_formatted_data
from api_client import course_api, user_api
from accounts.controller import get_current_course_for_user, get_current_program_for_user, clear_current_course_for_user
from accounts.middleware.thread_local import get_static_tab_context
from admin.controller import load_course

def user_program_data(request):
    ''' Makes user and program info available to all templates '''
    course = None
    program = None

    if request.user and request.user.id:
        # test loading the course to see if we can; if not, we destroy cached
        # information about current course and let the new course_id load again
        # in subsequent calls
        try:
            course_id = get_current_course_for_user(request)
            if not course_id is None:
                course = load_course(course_id)
        except:
            clear_current_course_for_user(request)
            course_id = get_current_course_for_user(request)

        if course_id:
            chapter_id = request.resolver_match.kwargs.get('chapter_id', None)
            page_id = request.resolver_match.kwargs.get('page_id', None)
            if page_id is None or chapter_id is None:
                course_id, chapter_id, page_id = locate_chapter_page(
                    request.user.id, course_id, None)
            course, current_chapter, current_sequential, current_page = build_page_info_for_course(
                course_id, chapter_id, page_id)

            program = get_current_program_for_user(request)

            # Inject formatted data for view (don't pass page_id in here - if needed it will be processed from elsewhere)
            _inject_formatted_data(program, course, None, get_static_tab_context())

            # Inject course progress for nav header
            load_course_progress(course, request.user.id)


    data = {
        "course": course,
        "program": program,
    }
    return data

def settings_data(request):
    ''' makes global settings available to all templates '''
    data = {
        "ga_tracking_id": settings.GA_TRACKING_ID,
        "ta_email_group": settings.TA_EMAIL_GROUP,
    }
    return data

