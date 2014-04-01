''' rendering templates from requests related to courses '''
import datetime
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from courses.controller import build_page_info_for_course, locate_chapter_page, program_for_course, update_bookmark

# Create your views here.


def _inject_formatted_data(program, course, page_id):
    for program_course in program.courses:
        program_course.nav_url = '/courses/{}'.format(program_course.course_id)
        if hasattr(program_course, 'start_date'):
            program_course.formatted_start_date = "{} {}".format(
                _("Available"),
                program_course.start_date.strftime('%B %d, %Y')
            )
            program_course.has_future_start_date = program_course.is_future_start()
        else:
            program_course.formatted_start_date = None
            program_course.percent_complete_message = "{}% {}".format(
                program_course.percent_complete,
                _("complete")
            )

    for idx, lesson in enumerate(course.chapters, start=1):
        lesson.index = idx
        lesson.tick_marks = []
        for i in range(1, 6):
            lesson.tick_marks.append(i * 20 <= 100)  # lesson.percent_complete
        found_current_page = False
        for page in lesson.pages:
            page.status_class = "complete"
            is_current = page_id == page.page_id
            if is_current:
                page.status_class = "current"
                found_current_page = True
            elif found_current_page:
                page.status_class = "incomplete"


@login_required
def homepage(request):
    '''
    Logged in user's homepage which will infer current program, course,
    etc. from user settings
    '''
    course_id, chapter_id, page_id = locate_chapter_page(
        request.user.id, None, None)

    course, current_chapter, current_page = build_page_info_for_course(
        course_id, chapter_id, page_id)

    program = program_for_course(request.user.id, course_id)

    # Inject formatted data for view
    _inject_formatted_data(program, course, page_id)

    data = {
        "user": request.user,
        "course": course,
        "current_chapter": current_chapter,
        "current_page": current_page,
        "program": program,
    }
    return render(request, 'courses/course_main.html.haml', data)


@login_required
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

    # Take note that the user has gone here
    program = program_for_course(request.user.id, course_id)
    program_id = program.program_id if program else None
    update_bookmark(
        request.user.id, program_id, course_id, chapter_id, page_id)

    # Inject formatted data for view
    _inject_formatted_data(program, course, page_id)

    data = {
        "user": request.user,
        "course": course,
        "current_chapter": current_chapter,
        "current_page": current_page,
        "program": program,
    }
    return render(request, 'courses/course_navigation.html.haml', data)


@login_required
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
