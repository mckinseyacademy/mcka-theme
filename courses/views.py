''' rendering templates from requests related to courses '''
import math
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _
from main.models import CuratedContentItem

from .controller import build_page_info_for_course, locate_chapter_page, program_for_course, update_bookmark, decode_id, encode_id
from lib.authorization import is_user_in_group
from api_client import course_api

# Create your views here.

def _inject_formatted_data(program, course, page_id):
    if program:
        for program_course in program.courses:
            program_course.nav_url = '/courses/{}'.format(program_course.id)
            program_course.course_class = ""
            if program_course.id == course.id:
                program_course.course_class = "current"
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
        lesson.tick_marks = [i * 20 <= 100 for i in range(1, 6)]
        found_current_page = False
        for sequential in lesson.sequentials:
            for page in sequential.pages:
                page.status_class = "complete"
                is_current = page_id == page.id
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
    course_id, chapter_id, page_id, chapter_position = locate_chapter_page(
        request.user.id, request.session.get("current_course_id"), None)

    if course_id:
        course, current_chapter, current_sequential, current_page = build_page_info_for_course(
            course_id, chapter_id, page_id, chapter_position)

        program = program_for_course(request.user.id, course_id)

        # Inject formatted data for view
        _inject_formatted_data(program, course, page_id)
    else:
        course = None
        current_chapter = None
        current_sequential = None
        current_page = None
        program = None

    course_slide_count = math.ceil(len(course.chapters)/float(5))

    data = {
        "user": request.user,
        "course": course,
        "current_chapter": current_chapter,
        "current_sequential": current_sequential,
        "current_page": current_page,
        "program": program,
        "is_admin": is_user_in_group(request.user, 'super_admin'),
        "articles": CuratedContentItem.objects.filter(content_type=CuratedContentItem.ARTICLE),
        "videos": CuratedContentItem.objects.filter(content_type=CuratedContentItem.VIDEO),
        "tweet": CuratedContentItem.objects.filter(content_type=CuratedContentItem.TWEET).last(),
        "quote": CuratedContentItem.objects.filter(content_type=CuratedContentItem.QUOTE).last(),
        "infographic": CuratedContentItem.objects.filter(content_type=CuratedContentItem.IMAGE).last(),
        "course_slide_count": range(0, int(course_slide_count))
    }
    return render(request, 'courses/course_main.haml', data)

@login_required
def navigate_to_page(request, course_id, current_view = 'overview'):
    # TODO - Figure out why nginx munges the id's so that we can get rid of this step
    course_id = decode_id(course_id)

    # Get course info
    course = course_api.get_course(course_id)

    # Take note that the user has gone here
    program = program_for_course(request.user.id, course_id)

    # Inject formatted data for view
    _inject_formatted_data(program, course, None)

    #remote_session_key = request.session.get("remote_session_key")
    #lms_base_domain = settings.LMS_BASE_DOMAIN
    #lms_sub_domain = settings.LMS_SUB_DOMAIN

    #vertical_usage_id = current_page.vertical_usage_id()

    data = {
        "user": request.user,
        "course": course,
        #"current_chapter": current_chapter,
        #"current_sequential": current_sequential,
        #"current_page": current_page,
        #"lms_base_domain": lms_base_domain,
        #"lms_sub_domain": lms_sub_domain,
        "program": program,
        #"remote_session_key": remote_session_key,
        #"vertical_usage_id": vertical_usage_id,
        "current_view": current_view,
        "current_template": "courses/course_{0}.haml".format(current_view),
    }

    if current_view == "overview":
        data["overview"] = course_api.get_course_overview(course_id)

    return render(request, 'courses/course_navigation.haml', data)

@login_required
def navigate_to_lesson_module(request, course_id, chapter_id, page_id):
    # TODO - Figure out why nginx munges the id's so that we can get rid of this step
    course_id = decode_id(course_id)
    chapter_id = decode_id(chapter_id)
    page_id = decode_id(page_id)

    ''' go to given page within given chapter within given course '''
    # Get course info
    course, current_chapter, current_sequential, current_page = build_page_info_for_course(
        course_id, chapter_id, page_id)

    # Take note that the user has gone here
    program = program_for_course(request.user.id, course_id)
    program_id = program.id if program else None
    request.session["current_course_id"] = course_id
    update_bookmark(
        request.user.id, program_id, course_id, chapter_id, current_sequential.id, page_id)

    # Inject formatted data for view
    _inject_formatted_data(program, course, page_id)

    remote_session_key = request.session.get("remote_session_key")
    lms_base_domain = settings.LMS_BASE_DOMAIN
    lms_sub_domain = settings.LMS_SUB_DOMAIN

    vertical_usage_id = current_page.vertical_usage_id()

    data = {
        "user": request.user,
        "course": course,
        "current_chapter": current_chapter,
        "current_sequential": current_sequential,
        "current_page": current_page,
        "lms_base_domain": lms_base_domain,
        "lms_sub_domain": lms_sub_domain,
        "program": program,
        "remote_session_key": remote_session_key,
        "vertical_usage_id": vertical_usage_id,
        "current_view": "lessons",
        "current_template": "courses/course_lessons.haml",
    }
    return render(request, 'courses/course_navigation.haml', data)

@login_required
def infer_chapter_navigation(request, course_id, chapter_id):
    '''
    Go to the bookmarked page for given chapter within given course
    If no chapter or course given, system tries to go to location within last
    visited course
    '''
    # TODO - Figure out why nginx munges the id's so that we can get rid of this step
    if course_id:
        course_id = decode_id(course_id)
    if chapter_id:
        chapter_id = decode_id(chapter_id)

    course_id, chapter_id, page_id, chapter_position = locate_chapter_page(
        request.user.id, course_id, chapter_id)

    if course_id and chapter_id and page_id:
        return HttpResponseRedirect(
            '/courses/{}/lessons/{}/module/{}'.format(
                encode_id(course_id),
                encode_id(chapter_id),
                encode_id(page_id)
            )
        )
    else:
        return HttpResponseRedirect(
            '/courses/{}/view/notready'.format(
                encode_id(course_id),
            )
        )

def infer_course_navigation(request, course_id):
    ''' handler to call infer chapter nav with no chapter '''
    return infer_chapter_navigation(request, course_id, None)

def infer_default_navigation(request):
    ''' handler to call infer chapter nav with no course '''
    return infer_chapter_navigation(request, None, None)
