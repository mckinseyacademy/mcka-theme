from django.conf import settings
from courses.controller import build_page_info_for_course, locate_chapter_page, program_for_course
from courses.views import _inject_formatted_data
from api_client import course_api
from accounts.controller import get_current_course_for_user


def user_program_data(request):
    ''' Makes user and program info available to all templates '''
    course = None
    current_chapter = None
    current_sequential = None
    current_page = None
    program = None

    if request.user and request.user.id:
        course_id = get_current_course_for_user(request)

        if course_id:
            course_id, chapter_id, page_id, chapter_position = locate_chapter_page(
                request.user.id, course_id, None)

        if course_id:
            course, current_chapter, current_sequential, current_page = build_page_info_for_course(
                course_id, chapter_id, page_id, chapter_position)

            program = program_for_course(request.user.id, course_id)

            # Inject formatted data for view
            _inject_formatted_data(program, course, page_id, course_api.get_course_tabs(course_id))

    data = {
        "course": course,
        "current_chapter": current_chapter,
        "current_sequential": current_sequential,
        "current_page": current_page,
        "program": program,
    }
    return data


def settings_data(request):
    ''' makes global settings available to all templates '''
    data = {
        "ga_tracking_id": settings.GA_TRACKING_ID,
    }
    return data

