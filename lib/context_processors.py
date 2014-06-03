from django.conf import settings
from courses.controller import build_page_info_for_course, locate_chapter_page, program_for_course

from courses.views import _inject_formatted_data
from api_client import course_api, user_api
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


            # Inject lesson assessment scores
            assesment_scores = []

            gradebook = user_api.get_user_gradebook(request.user.id, course.id)
            for lesson in gradebook.courseware_summary:
                points = 0
                max_points = 0

                for section in lesson.sections:
                    points += section.section_total[0]
                    max_points += section.section_total[1]

                if max_points > 0:
                    percent = int(round(100*points/float(max_points)))
                else:
                    percent = None

                assesment_scores.append(percent)

            length = len(assesment_scores)

            for i, lesson in enumerate(course.chapters):
                lesson.assesment_score = assesment_scores[i] if i < length else None


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
        "ta_email_group": settings.TA_EMAIL_GROUP,
    }
    return data

