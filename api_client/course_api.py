''' API calls with respect to courses '''
from django.conf import settings

from api_error import api_error_protect

from .json_object import CategorisedJsonParser
from .json_object import CategorisedJsonObject
from .json_object import JsonParser as JP
from .json_requests import GET
from .json_requests import POST

from . import course_models

COURSEWARE_API = 'api/courses'

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

@api_error_protect
def get_course_list():
    '''
    Retrieves list of courses from openedx server
    '''
    response = GET('{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API)
    )
    return CJP.from_json(response.read())

@api_error_protect
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

@api_error_protect
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

@api_error_protect
def get_course_syllabus(course_id):
    '''
    Retrieves course syllabus information from the API for specified course
    '''
    tabs = get_course_tabs(course_id)
    if "syllabus" in tabs:
        return tabs["syllabus"].content
    else:
        return None


@api_error_protect
def get_course_news(course_id):
    '''
    Retrieves course updates from the API for specified course
    '''
    response = GET('{}/{}/{}/updates?parse=true'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id)
    )
    return JP.from_json(response.read()).postings

@api_error_protect
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


@api_error_protect
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

@api_error_protect
def get_user_list(course_id, program_id = None, client_id = None):

    return JP.from_json(get_user_list_json(course_id, program_id, client_id), course_models.CourseEnrollmentList).enrollments

@api_error_protect
def add_group_to_course_content(group_id, course_id, content_id):
    ''' associate group to specific course '''

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

@api_error_protect
def get_users_content_filtered(course_id, content_id, params):
    ''' filter and get course content'''

    paramStr = ''
    for param in params:
        paramStr = paramStr + param['key'] + '=' + param['value']

    response = GET(
        '{}/{}/{}/content/{}/users?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            content_id,
            paramStr,
        )
    )

    return JP.from_json(response.read())

@api_error_protect
def get_course_content_groups(course_id, content_id):
    ''' fetch associates groups to specific content within specific course '''

    response = GET(
        '{}/{}/{}/content/{}/groups'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            content_id,
        )
    )

    return JP.from_json(response.read(), course_models.CourseContentGroup)

