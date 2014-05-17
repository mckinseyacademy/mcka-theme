from courses.controller import build_page_info_for_course, locate_chapter_page, program_for_course
from courses.views import _inject_formatted_data

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
            _inject_formatted_data(program, course, page_id)

    data = {
        "course": course,
        "current_chapter": current_chapter,
        "current_sequential": current_sequential,
        "current_page": current_page,
        "program": program,
    }
    return data
