from django.conf import settings
from courses.controller import build_page_info_for_course, locate_chapter_page

from courses.views import _inject_formatted_data
from api_client import course_api, user_api
from accounts.controller import get_current_course_for_user, get_current_program_for_user


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
            course, current_chapter, current_sequential, current_page = build_page_info_for_course(
                course_id, chapter_id, page_id, chapter_position)

            program = get_current_program_for_user(request)

            # Inject formatted data for view
            _inject_formatted_data(program, course, page_id, course_api.get_course_tabs(course_id))


            # Inject lesson assessment scores
            assesments = {}

            gradebook = user_api.get_user_gradebook(request.user.id, course.id)
            if gradebook.courseware_summary:
                for lesson in gradebook.courseware_summary:
                    percent = None
                    for section in lesson.sections:
                        if section.graded == True:
                            points = section.section_total[0]
                            max_points = section.section_total[1]
                            if max_points > 0:
                                percent = int(round(100*points/max_points))
                            else:
                                percent = 0
                            assesments[section.url_name] = percent

            for lesson in course.chapters:
                lesson.assesment_score = None
                for sequential in lesson.sequentials:
                    url_name = sequential.id.split('/')[-1]
                    if url_name in assesments:
                        lesson.assesment_score = assesments[url_name]
                        break


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

