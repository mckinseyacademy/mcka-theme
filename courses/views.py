from django.http import HttpResponse, HttpResponseRedirect
import haml_mako.templates as haml

from controller import build_page_info_for_course, locate_chapter_page

# Create your views here.


def navigate_to_page(request, course_id, chapter_id, page_id):
    course, current_chapter, current_page = build_page_info_for_course(course_id, chapter_id, page_id);

    template = haml.get_haml_template('courses/course_main.html.haml')
    return HttpResponse(template.render_unicode(user=request.user, course=course, current_chapter=current_chapter, current_page=current_page))

def infer_chapter_navigation(request, course_id, chapter_id):
    course_id, chapter_id, page_id = locate_chapter_page(request.user.id, course_id, chapter_id)
    
    return HttpResponseRedirect('/courses/{}/lessons/{}/module/{}'.format(course_id, chapter_id, page_id))

def infer_course_navigation(request, course_id):
    return infer_chapter_navigation(request, course_id, None)

def infer_default_navigation(request):
    return infer_chapter_navigation(request, None, None)
