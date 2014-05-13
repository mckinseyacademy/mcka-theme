''' API calls with respect to courses '''
from .json_object import CategorisedJsonParser
from .json_object import CategorisedJsonObject
from .json_object import JsonParser as JP
from . import course_models
from .json_requests import GET
from .json_requests import POST
from urllib2 import HTTPError

from django.conf import settings

COURSEWARE_API = 'api/courses'
GROUP_PROJECT_IDENTIFIER = 'GROUP_PROJECT'

OBJECT_CATEGORY_MAP = {
    # Core objects for our desire
    "course": course_models.Course,
    "chapter": course_models.Chapter,
    "sequential": course_models.Sequential,
    "vertical": course_models.Page,

    # Others that may become important in the future:
    "html": CategorisedJsonObject,
    "video": CategorisedJsonObject,
    "discussion": CategorisedJsonObject,
    "problem": CategorisedJsonObject,
}

CJP = CategorisedJsonParser(OBJECT_CATEGORY_MAP)

def get_course_list():
    '''
    Retrieves list of courses from openedx server
    '''
    response = GET('{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API)
    )
    return CJP.from_json(response.read())

def get_course_overview(course_id):
    '''
    Retrieves course overview information from the API for specified course
    '''
    response = GET('{}/{}/{}/overview?parse=true'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id)
    )

    overview = CJP.from_json(response.read())
    about = [item for item in overview.sections if getattr(item, "class") == "about"]
    if len(about) > 0:
        overview.about = about[0].body

    faculty = [item for item in overview.sections if getattr(item, "class") == "course-staff"]
    if len(faculty) > 0:
        overview.faculty = faculty[0].articles
        for idx, teacher in enumerate(overview.faculty):
            teacher.idx = idx

    what_you_will_learn = [item for item in overview.sections if getattr(item, "class") == "what-you-will-learn"]
    if len(what_you_will_learn) > 0:
        overview.what_you_will_learn = what_you_will_learn[0].body

    return overview

def get_course_tabs(course_id):
    '''
    Returns map of tab content key'd on "name" attribute
    '''
    response = GET('{}/{}/{}/static_tabs?detail=true'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id)
    )
    
    tab_array = JP.from_json(response.read(), course_models.CourseTabs).tabs

    return {tab.name.lower(): tab for tab in tab_array}

def get_course_syllabus(course_id):
    '''
    Retrieves course syllabus information from the API for specified course
    '''
    tabs = get_course_tabs(course_id)
    if "syllabus" in tabs:
        return tabs["syllabus"].content
    else:
        return None


def get_course_news(course_id):
    '''
    Retrieves course updates from the API for specified course
    '''
    response = GET('{}/{}/{}/updates?parse=true'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id)
    )
    return CJP.from_json(response.read()).postings

def get_course(course_id, depth = 3):
    '''
    Retrieves course structure information from the API for specified course
    '''
    response = GET('{}/{}/{}?depth={}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        depth)
    )

    # Load the depth from the API
    course = CJP.from_json(response.read())
    course.chapters = [content_module for content_module in course.content if content_module.category == "chapter"]

    for chapter in course.chapters:
        chapter.sequentials = [content_child for content_child in chapter.children if content_child.category == "sequential"]
        chapter.is_released = True

        for sequential in chapter.sequentials:
            sequential.pages = [content_child for content_child in sequential.children if content_child.category == "vertical"]

    return course

def load_course(course_id):
    '''
    Gets the course from the API, and performs any post-processing for Apros specific purposes
    '''
    course = get_course(course_id)

    # Special chapter for Group Project
    group_projects = [chapter for chapter in course.chapters if chapter.name.startswith(GROUP_PROJECT_IDENTIFIER)]
    if len(group_projects) > 0:
        course.group_project = group_projects[0]
        course.chapters = [chapter for chapter in course.chapters if chapter.id != course.group_project.id]
        course.group_project.name = course.group_project.name(len(GROUP_PROJECT_IDENTIFIER))

    return course

def get_user_list_json(course_id, program_id = None, client_id = None):
    '''
    Retrieves course user list structure information from the API for specified course
    '''
    response = GET('{}/{}/{}/users?project={}&client={}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API, 
        course_id, 
        program_id, 
        client_id)
    )

    return response.read()

def get_user_list(course_id):

    return JP.from_json(get_user_list_json(course_id), course_models.CourseEnrollmentList).enrollments

def add_workgroup_to_course(group_id, course_id, content_id):
    ''' associate workgroup to specific course '''

    data = {
        'course_id': course_id, 
        'group_id': group_id, 
        'content_id': content_id, 
    }

    response = POST(
        '{}/{}/{}/content/{}/groups'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API, 
            course_id,
            content_id,
        ), 
        data
    )

    return JP.from_json(response.read())

