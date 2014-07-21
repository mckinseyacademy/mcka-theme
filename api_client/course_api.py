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

    video = [item for item in overview.sections if getattr(item, "class") == "overview_video"]
    if len(video) > 0:
        overview.video = getattr(video[0].attributes, 'data-video-id')

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
def get_course_content(course_id, content_id):
    ''' returns course content'''
    response = GET(
        '{}/{}/{}/content/{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            content_id,
        )
    )

    return JP.from_json(response.read())

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
def get_users_list_in_organizations(course_id, organizations):
    '''
    Retrieves course user list structure information from the API for specified course
    '''
    response = GET('{}/{}/{}/users?organizations={}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        organizations,)
    )

    return JP.from_json(response.read(), course_models.CourseEnrollmentList).enrollments


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
def get_users_content_filtered(course_id, content_id, params=[]):
    ''' filter and get course content'''

    paramStrs = [param['key'] + '=' + param['value'] for param in params]
    if len(paramStrs) > 0:
        paramStr = '&'.join(paramStrs)
    else:
        paramStr = ''

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
    print '{}/{}/{}/content/{}/groups'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            content_id,
        )
    response = GET(
        '{}/{}/{}/content/{}/groups'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            content_id,
        )
    )

    return JP.from_json(response.read(), course_models.CourseContentGroup)

@api_error_protect
def get_course_completions(course_id, user_id):
    ''' fetch course module completion list '''

    response = GET(
        '{}/{}/{}/completions?user_id={}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            user_id,
        )
    )

    return JP.from_json(response.read())

@api_error_protect
def get_course_metrics(course_id):
    ''' retrieves course metrics '''

    url = '{}/{}/{}/metrics'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id
    )

    response = GET(url)
    return JP.from_json(response.read())

@api_error_protect
def get_course_metrics_by_city(course_id, cities=None):
    ''' retrieves course metrics '''
    if cities == None:
        url = '{}/{}/{}/metrics/cities'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id
        )
    else:
        url = '{}/{}/{}/metrics/cities?city={}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            cities
        )

    response = GET(url)
    return JP.from_json(response.read()).results



@api_error_protect
def get_course_metrics_proficiency(course_id, user_id=None, count=3):
    ''' retrieves users who are leading in terms of points_scored'''

    url = '{}/{}/{}/metrics/proficiency/leaders?count={}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        count
    )

    if user_id:
        url += '&user_id={}'.format(user_id)

    response = GET(url)
    return JP.from_json(response.read())

@api_error_protect
def get_course_metrics_completions(course_id, user_id=None, count=3):
    ''' retrieves users who are leading in terms of  course module completions '''

    url = '{}/{}/{}/metrics/completions/leaders?count={}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        count
    )

    if user_id:
        url += '&user_id={}'.format(user_id)

    response = GET(url)
    return JP.from_json(response.read())


@api_error_protect
def get_course_social_metrics(course_id):
    ''' fetch social metrics for course '''

    response = GET(
        '{}/{}/{}/metrics/social/'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
        )
    )

    return JP.from_json(response.read())
