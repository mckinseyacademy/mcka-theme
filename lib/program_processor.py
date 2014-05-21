from courses.controller import build_page_info_for_course, locate_chapter_page, program_for_course
#from courses.views import _inject_formatted_data
import datetime
import math

def user_program(request):
    course = None
    current_chapter = None
    current_sequential = None
    current_page = None
    program = None

    if request.user and request.user.id:
        course_id, chapter_id, page_id, chapter_position = locate_chapter_page(
            request.user.id, request.session.get("current_course_id"), None)

        if course_id:
            course, current_chapter, current_sequential, current_page = build_page_info_for_course(
                course_id, chapter_id, page_id, chapter_position)

            program = program_for_course(request.user.id, course_id)

            # Inject formatted data for view
           # _inject_formatted_data(program, course, page_id)
    if program.id is not 'NO_PROGRAM':
        if program.start_date > datetime.datetime.today():
            days = str(int(math.floor(((program.start_date - datetime.datetime.today()).total_seconds()) / 3600 / 24))) + ' day'
            if days > 1:
                days = days + 's'
            program.popup_title = "Welcome to McKinsey Academy"
            program.popup_description = "Your program will start in {}. Please explore the site to learn more about the expirience in the meantime.".format(days)
        

    data = {
        "course": course,
        "current_chapter": current_chapter,
        "current_sequential": current_sequential,
        "current_page": current_page,
        "program": program,
    }
    return data
