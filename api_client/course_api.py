''' API calls with respect to courses '''
from django.conf import settings
from urllib import urlencode

from api_error import api_error_protect

from .json_object import CategorisedJsonParser
from .json_object import CategorisedJsonObject
from .json_object import JsonParser as JP
from .json_object import JsonObject
from .json_requests import GET
from .json_requests import POST

from .group_models import GroupInfo
from . import course_models

COURSEWARE_API = getattr(settings, 'COURSEWARE_API', 'api/server/courses')

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
    qs_params = {"page_size": 0}
    response = GET('{}/{}?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            urlencode(qs_params)
        )
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
def get_course(course_id, depth=3):
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
def get_courses(**kwargs):
    '''
    Retrieves course structure information from the API for specified courses
    '''
    qs_params = {"page_size": 0}

    for karg in kwargs:
        if isinstance(kwargs[karg], list):
            qs_params[karg] = ",".join(kwargs[karg])
        else:
            qs_params[karg] = kwargs[karg]

    response = GET('{}/{}/?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        urlencode(qs_params))
    )

    return CJP.from_json(response.read())

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
def get_course_groups(course_id, group_type=None, group_object=GroupInfo, *args, **kwargs):
    ''' get groups associated with this course '''
    qs_params = {}
    qs_params.update(kwargs)

    if group_type:
        qs_params["type"] = group_type

    url = '{}/{}/{}/groups'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
    )

    if len(qs_params.keys()) > 0:
        url += "?{}".format(urlencode(qs_params))

    response = GET(url)
    return JP.from_json(response.read(), group_object)

@api_error_protect
def get_user_list_json(course_id, program_id = None):
    '''
    Retrieves course user list structure information from the API for specified course
    '''
    qs_params = {}
    if program_id:
        qs_params['project'] = program_id

    response = GET('{}/{}/{}/users?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            urlencode(qs_params),
        )
    )

    return response.read()

@api_error_protect
def get_user_list(course_id, program_id = None):

    return JP.from_json(get_user_list_json(course_id, program_id), course_models.CourseEnrollmentList).enrollments

@api_error_protect
def get_users_list_in_organizations(course_id, organizations):
    '''
    Retrieves course user list structure information from the API for specified course
    '''
    qs_params = {"organizations": organizations}
    response = GET('{}/{}/{}/users?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            urlencode(qs_params),
        )
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
def get_users_content_filtered(course_id, content_id, *args, **kwargs):
    ''' filter and get course content'''

    qs_params = {}
    qs_params.update(kwargs)
    response = GET(
        '{}/{}/{}/content/{}/users?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            content_id,
            urlencode(qs_params),
        )
    )

    return JP.from_json(response.read())

@api_error_protect
def get_users_filtered_by_group(course_id, group_ids):
    ''' filter and get course users'''

    qs_params = {"groups": group_ids}
    response = GET(
        '{}/{}/{}/users?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            urlencode(qs_params),
        )
    )

    return JP.from_json(response.read()).enrollments

@api_error_protect
def get_users_filtered_by_role(course_id):
    ''' filter and get course users'''

    response = GET(
        '{}/{}/{}/roles'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
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

@api_error_protect
def get_course_completions(course_id, user_id=None):
    ''' fetch course module completion list '''
    qs_params = {"page_size": 0}
    if user_id:
        qs_params["user_id"] = user_id

    url = '{}/{}/{}/completions/?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params),
    )
    response = GET(url)

    return JP.from_json(response.read())

@api_error_protect
def get_course_metrics(course_id, *args, **kwargs):
    ''' retrieves course metrics '''

    qs_params = {}

    for karg in kwargs:
        if isinstance(kwargs[karg], list):
            qs_params[karg] = ",".join(kwargs[karg])
        else:
            qs_params[karg] = kwargs[karg]

    url = '{}/{}/{}/metrics/?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params),
    )

    response = GET(url)
    return JP.from_json(response.read(), course_models.CourseMetrics)

@api_error_protect
def get_course_metrics_by_city(course_id, cities=None):
    ''' retrieves course metrics '''
    qs_params = {"page_size": 0}
    if cities:
        qs_params["city"] = cities

    url = '{}/{}/{}/metrics/cities/?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params),
    )
    response = GET(url)

    return JP.from_json(response.read())


@api_error_protect
def get_course_metrics_grades(course_id, grade_object_type=JsonObject, **kwargs):
    ''' retrieves users who are leading in terms of points_scored'''

    qs_params = {"count": 3}
    qs_params.update(kwargs)

    url = '{}/{}/{}/metrics/grades/leaders?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params),
    )
    response = GET(url)

    return JP.from_json(response.read(), grade_object_type)

@api_error_protect
def get_course_metrics_completions(course_id, completions_object_type=JsonObject, **kwargs):
    ''' retrieves users who are leading in terms of  course module completions '''

    qs_params = {"count": 3}
    qs_params.update(kwargs)

    url = '{}/{}/{}/metrics/completions/leaders?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params),
    )
    response = GET(url)

    return JP.from_json(response.read(), completions_object_type)

@api_error_protect
def get_course_social_metrics(course_id, organization_id=None):
    ''' fetch social metrics for course '''
    qs_params = {}
    if organization_id:
        qs_params['organization'] = organization_id

    response = GET(
        '{}/{}/{}/metrics/social/?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            urlencode(qs_params)
        )
    )

    return JP.from_json(response.read())


@api_error_protect
def get_course_time_series_metrics(course_id, start_date, end_date, time_series_object=course_models.CourseTimeSeriesMetrics, *args, **kwargs):
    ''' a list of Metrics for the specified Course in time series format '''
    qs_params = {
        'start_date': start_date,
        'end_date': end_date
    }
    qs_params.update(kwargs)

    url = '{}/{}/{}/time-series-metrics?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params),
    )
    response = GET(url)

    return JP.from_json(response.read(), time_series_object)


@api_error_protect
def get_course_projects(course_id, page_size=0, project_object=JsonObject):
    ''' Fetches all the project objects for the course '''

    qs_params = {"page_size": page_size}
    url = '{}/{}/{}/projects/?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params),
    )
    response = GET(url)

    return JP.from_json(response.read(), project_object)

@api_error_protect
def get_module_details(module_uri, include_fields = [], module_object = None):
    ''' Fetches the details of the object at the specific uri with the named custom fields'''

    qs_params = {"include_fields": ",".join(include_fields)} if len(include_fields) > 0 else None

    if qs_params:
        module_uri += "?{}".format(urlencode(qs_params))

    response = GET(module_uri)

    if module_object:
        return JP.from_json(response.read(), module_object)

    return CJP.from_json(response.read())

@api_error_protect
def get_course_content_detail(course_id, content_id, include_fields = [], module_object = None):
    ''' Fetches the details of the object at the specific uri with the named custom fields'''

    url = '{}/{}/{}/content/{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        content_id,
    )

    return get_module_details(url, include_fields, module_object)
