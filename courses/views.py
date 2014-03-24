import haml
import mako.template
from django.http import HttpResponse, HttpResponseRedirect
from api_client import course_api, user_api

import haml_mako.templates as haml

# Create your views here.

def _is_int_equal(elem1, elem2):
    result = False
    try:
        result = (int(elem1) == int(elem2))
    except:
        result = (elem1 == elem2)

    return result


def navigate_to_page(request, course_id, chapter_id, page_id):
    course = course_api.get_course(course_id)

    # something sensible if we fail...
    current_chapter = course.chapters[0]
    current_page = None

    prev_url = None
    next_url = None
    last_page = None
    for chapter in course.chapters:
        chapter.navigation_url = '/courses/{}/lessons/{}'.format(course_id, chapter.chapter_id)
        if _is_int_equal(chapter.chapter_id, chapter_id):
            current_chapter = chapter

        for page in chapter.pages:
            page.prev_url = prev_url
            page.next_url = None
            page.navigation_url = '/courses/{}/lessons/{}/module/{}'.format(course_id, chapter_id, page.page_id)
            if None != last_page:
                last_page.next_url = page.navigation_url
            prev_url = page.navigation_url
            last_page = page
            if _is_int_equal(page.page_id, page_id):
                current_page = page

    if not current_page:
        current_page = current_chapter.pages[0]

    template = haml.get_haml_template('courses/course_main.html.haml')
    return HttpResponse(template.render_unicode(user=request.user, course=course, current_chapter=current_chapter, current_page=current_page))


def infer_chapter_navigation(request, course_id, chapter_id):
    user_status = user_api.get_user_course_status(request.user.id)
    if not course_id:
        course_id = user_status.current_course_id

    bookmark = user_status.get_bookmark_for_course(course_id)
    if None != bookmark and (chapter_id == None or bookmark.chapter_id == chapter_id):
        return HttpResponseRedirect('/courses/{}/lessons/{}/module/{}'.format(course_id, bookmark.chapter_id, bookmark.page_id))

    course = course_api.get_course(course_id)
    chapter = course.chapters[0]
    if chapter_id:
        for course_chapter in course.chapters:
            if course_chapter.chapter_id == chapter_id:
                chapter = course_chapter
                break
    page = chapter.pages[0]

    return HttpResponseRedirect('/courses/{}/lessons/{}/module/{}'.format(course_id, chapter.chapter_id, page.page_id))


def infer_course_navigation(request, course_id):
    return infer_chapter_navigation(request, course_id, None)


def infer_default_navigation(request):
    return infer_chapter_navigation(request, None, None)
