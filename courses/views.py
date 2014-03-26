''' rendering templates from requests related to courses '''
from django.http import HttpResponse, HttpResponseRedirect
import haml_mako.templates as haml

from courses.controller import build_page_info_for_course, locate_chapter_page, program_for_course, update_bookmark

# Create your views here.


def navigate_to_page(request, course_id, chapter_id, page_id):
    ''' go to given page within given chapter within given course '''
    if course_id:
        course_id = int(course_id)
    if chapter_id:
        chapter_id = int(chapter_id)
    if page_id:
        page_id = int(page_id)

    # Get course info
    course, current_chapter, current_page = build_page_info_for_course(
        course_id, chapter_id, page_id)

    course.program = program_for_course(request.user.id, course_id)

    # Take note that the user has gone here
    program_id = course.program.program_id if course.program else None
    update_bookmark(
        request.user.id, program_id, course_id, chapter_id, page_id)

    template = haml.get_haml_template('courses/course_main.html.haml')
    return HttpResponse(
        template.render_unicode(
                user=request.user,
                course=course,
                current_chapter=current_chapter,
                current_page=current_page
            )
        )


def infer_chapter_navigation(request, course_id, chapter_id):
    '''
    Go to the bookmarked page for given chapter within given course
    If no chapter or course given, system tries to go to location within last
    visited course
    '''
    if course_id:
        course_id = int(course_id)
    if chapter_id:
        chapter_id = int(chapter_id)

    course_id, chapter_id, page_id = locate_chapter_page(
        request.user.id, course_id, chapter_id)

    return HttpResponseRedirect(
        '/courses/{}/lessons/{}/module/{}'.format(
            course_id,
            chapter_id,
            page_id
        )
    )


def infer_course_navigation(request, course_id):
    ''' handler to call infer chapter nav with no chapter '''
    return infer_chapter_navigation(request, course_id, None)


def infer_default_navigation(request):
    ''' handler to call infer chapter nav with no course '''
    return infer_chapter_navigation(request, None, None)
