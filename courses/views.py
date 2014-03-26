from django.http import HttpResponse, HttpResponseRedirect
import haml_mako.templates as haml

from controller import build_page_info_for_course, locate_chapter_page, program_for_course, update_bookmark

# Create your views here.


def navigate_to_page(request, course_id, chapter_id, page_id):
    # Get course info
    course, current_chapter, current_page = build_page_info_for_course(course_id, chapter_id, page_id);

    course.program = program_for_course(request.user.id, course_id)

    # Take note that the user has gone here
    program_id = course.program.program_id if course.program else None
    update_bookmark(request.user.id, program_id, course_id, chapter_id, page_id)

    template = haml.get_haml_template('courses/course_main.html.haml')
    return HttpResponse(template.render_unicode(user=request.user, course=course, current_chapter=current_chapter, current_page=current_page))

def infer_chapter_navigation(request, course_id, chapter_id):
    course_id, chapter_id, page_id = locate_chapter_page(request.user.id, course_id, chapter_id)
    
    return HttpResponseRedirect('/courses/{}/lessons/{}/module/{}'.format(course_id, chapter_id, page_id))

def infer_course_navigation(request, course_id):
    return infer_chapter_navigation(request, course_id, None)

def infer_default_navigation(request):
    return infer_chapter_navigation(request, None, None)

def program_menu(request):
    # Get course info
    course, current_chapter, current_page = build_page_info_for_course(2, 11, 111);

    course.program = program_for_course(request.user.id, 2)

    template = haml.get_haml_template('courses/content_page/program_menu.html.haml')
    return HttpResponse(template.render_unicode(user=request.user, course=course, current_chapter=current_chapter, current_page=current_page))
