''' API calls with respect to courses '''

import json
from urllib import urlencode

from django.conf import settings

from api_data_manager.course_data import COURSE_PROPERTIES
from api_data_manager.decorators import course_api_cache_wrapper

from .api_error import api_error_protect
from . import course_models
from .group_models import GroupInfo
from .json_object import CategorisedJsonParser
from .json_object import CategorisedJsonObject
from .json_object import JsonParser as JP
from .json_object import JsonObject
from .json_requests import GET, POST
from .oauth2_requests import get_oauth2_session
from . import user_models


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
def get_course_list(ids=None):
    '''
    Retrieves list of courses from openedx server
    '''
    qs_params = {"page_size": 0}
    if ids:
        qs_params['course_id'] = ",".join(ids)

    response = GET('{}/{}?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            urlencode(qs_params)
        )
    )
    return CJP.from_json(response.read())


@api_error_protect
def get_course_list_in_pages(ids=None, page_size=100):
    '''
    Retrieves list of courses from openedx server
    '''
    qs_params = {}
    if ids:
        qs_params['course_id'] = ",".join(ids)
        qs_params["page_size"] = 0
    else:
        qs_params["page"]=1
        qs_params["page_size"] = page_size
    response = GET('{}/{}?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            urlencode(qs_params)
        )
    )
    data = json.loads(response.read())
    if data.get("results", None):
        data_range = data.get("num_pages", 1)
        data = []
        for index in range(1, data_range+1):
            qs_params["page"]=index
            response = GET('{}/{}?{}'.format(
                    settings.API_SERVER_ADDRESS,
                    COURSEWARE_API,
                    urlencode(qs_params)
                )
            )
            data_fetched = json.loads(response.read()).get("results", [])
            data.extend(data_fetched)
    data = json.dumps(data)
    return CJP.from_json(data)


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


def tabs_post_process(tabs):
    tab_array = tabs.tabs
    return {tab.name.lower(): tab for tab in tab_array}


@api_error_protect
@course_api_cache_wrapper(
    parse_method=JP.from_json,
    parse_object=course_models.CourseTabs,
    property_name=COURSE_PROPERTIES.TABS,
    post_process_method=tabs_post_process,
)
def get_course_tabs(course_id, details=True):
    '''
    Returns map of tab content key'd on "name" attribute
    '''
    param = ""
    if details:
        param = "?detail=true"
    response = GET('{}/{}/{}/static_tabs{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        param)
    )

    return response.read()


def course_tab_post_process(tab):
    tab.name = tab.name.lower()
    return tab


@api_error_protect
@course_api_cache_wrapper(
    parse_method=JP.from_json,
    parse_object=course_models.CourseTabs,
    property_name=COURSE_PROPERTIES.TAB_CONTENT,
    post_process_method=course_tab_post_process
)
def get_course_tab(course_id, tab_id=None, name=None):
    """
    Return static tab content requested by tab name or id.
    """
    query = name if name else tab_id
    response = GET('{}/{}/{}/static_tabs/{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        query)
    )
    return response.read()


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


def course_detail_processing(course):
    course.chapters = []
    if hasattr(course, 'content'):
        course.chapters = [content_module for content_module in course.content if content_module.category == "chapter"]

    for chapter in course.chapters:
        chapter.sequentials = [content_child for content_child in chapter.children if
                               content_child.category == "sequential"]
        chapter.is_released = True

        for sequential in chapter.sequentials:
            pages = []
            if hasattr(sequential, 'children'):
                pages = [content_child for content_child in sequential.children if content_child.category == "vertical"]
            sequential.pages = pages

    return course


@api_error_protect
@course_api_cache_wrapper(
    parse_method=CJP.from_json,
    parse_object=None,
    property_name=COURSE_PROPERTIES.DETAIL,
    post_process_method=course_detail_processing
)
def get_course(course_id, depth=settings.COURSE_DEFAULT_DEPTH, user=None):
    '''
    Retrieves course structure information from the API for specified course
    and user. (e.g. staff may see more content than students)

    Refer to `course_api_cache_wrapper` for cache implementation as it reduces
    the API calls by limiting it to staff/non-staff user types
    '''
    edx_oauth2_session = get_oauth2_session()
    username = None
    if user:
        # user was passed; it could be a dict or an object.
        try:
            username = user.username
        except AttributeError:
            username = user.get('username')

    url = '{}/{}/{}?depth={}{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        depth,
        '&username={}'.format(username) if username else ''
    )

    response = edx_oauth2_session.get(url=url)

    # Load the depth from the API
    return response.content


@api_error_protect
def get_course_shallow(course_id):
    '''
    Retrieves course structure information from the API for specified course
    '''
    edx_oauth2_session = get_oauth2_session()
    url = '{}/{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id
    )
    response = edx_oauth2_session.get(url)

    return response.json()

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
def get_user_list_json(course_id, program_id = None, page_size=0):
    '''
    Retrieves course user list structure information from the API for specified course
    '''
    qs_params = {"page_size": page_size}
    if program_id:
        qs_params['project'] = program_id

    url = '{}/{}/{}/users?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params),
    )

    if page_size != 0:
        results = []
        response = GET(url)
        data = json.loads(response.read())
        pages = data['num_pages']
        for x in range(0, pages):
            result = data['results']
            results.extend(result)
            if data['next']:
                response =  GET(data['next'])
                data = json.loads(response.read())
        return json.dumps(results)
    else:
        response = GET(url)
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
def get_user_lesson_completion(username, course_id, edx_oauth2_session=None):
    ''' Query the LMS for completion data. '''
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()
    url = '{}/api/completion/v0/course/{}/?username={}&requested_fields=chapter'.format(
        settings.API_SERVER_ADDRESS,
        course_id,
        username
    )
    response = edx_oauth2_session.get(url)
    return response.json()


@api_error_protect
def get_course_completions(course_id, user_id=None, page_size=0):
    ''' fetch course module completion list '''
    qs_params = {"page_size": page_size}
    if user_id:
        qs_params["user_id"] = user_id

    url = '{}/{}/{}/completions/?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params),
    )
    if page_size != 0:
        results = []
        response = GET(url)
        data = json.loads(response.read())
        pages = data['num_pages']
        for _ in range(0, pages):
            result = data['results']
            results.extend(result)
            if data['next']:
                response = GET(data['next'])
                data = json.loads(response.read())
        return JP.from_json(json.dumps(results))
    else:
        response = GET(url)
        return JP.from_json(response.read())


@api_error_protect
def get_course_metrics(course_id, *args, **kwargs):
    """
    retrieves course metrics
    `metrics_required` param can be passed to course metrics api to get additional metrics
    possible values for `metrics_required param` are
    ``` users_started,modules_completed,users_completed,thread_stats ```
    :param course_id:
    :param args:
    :param kwargs:
    :return: course metrics objects having these possible course metrics
        grade_cutoffs, users_enrolled, users_started, users_not_started, modules_completed,users_completed
        and thread_stats. where thread_stats has num_active_threads and num_threads
    """

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
def get_social_enagement_leaderboard(course_id, count, **kwargs):
    """
    Get social engagement leaderboard for given course and user's position in leaderboard
    """
    qs_params = {"count": count}
    qs_params.update(kwargs)

    response = GET(
        '{}/{}/{}/metrics/social/leaders/?{}'.format(
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


@api_error_protect
def get_course_navigation(course_id, target_location_id):
    url = '{}/{}/{}/navigation/{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        target_location_id,
    )

    response = GET(url)

    return JP.from_json(response.read())


@api_error_protect
def get_courses_list(getParameters):
    '''
    Retrieves list of courses from openedx server
    '''
    response = GET('{}/{}?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            urlencode(getParameters)
        )
    )
    return json.loads(response.read())


@api_error_protect
def get_course_details(course_id):
    edx_oauth2_session = get_oauth2_session()

    url = '{}/{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id
    )

    response = edx_oauth2_session.get(url)

    return response.json()


@api_error_protect
def get_course_details_users(course_id, qs_params = ''):

    response = GET('{}/{}/{}/users?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params))
    )

    return json.loads(response.read())


@api_error_protect
def get_course_details_groups(course_id):

    response = GET('{}/{}/{}/groups'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id)
    )

    return json.loads(response.read())


@api_error_protect
def get_course_details_users_groups(course_id, groups_ids):
    ''' filter and get course users'''

    response = GET(
        '{}/{}/{}/users?groups={}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            groups_ids
        )
    )

    return json.loads(response.read())


@api_error_protect
def get_course_details_metrics_completions(course_id, count):

    response = GET(
        '{}/{}/{}/metrics/completions/leaders?count={}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            count
        )
    )

    return json.loads(response.read())


@api_error_protect
def get_course_module_completions(course_id, user_id, content_id):

    response = GET(
        '{}/{}/{}/completions/?user_id={}&content_id={}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            user_id,
            content_id,
        )
    )

    return json.loads(response.read())


@api_error_protect
def get_course_details_metrics_grades(course_id, count):

    response = GET(
        '{}/{}/{}/metrics/grades/leaders?count={}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            count
        )
    )

    return json.loads(response.read())


@api_error_protect
def get_course_details_metrics_social(course_id, qs_params = ''):
    ''' fetch social metrics for course '''

    response = GET(
        '{}/{}/{}/metrics/social/?'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            urlencode(qs_params)
        )
    )

    return json.loads(response.read())


@api_error_protect
def get_course_details_completions_leaders(course_id, organization_id='', **kwargs):
    qs_params = {"organizations": organization_id}
    qs_params.update(kwargs)

    response = GET(
        '{}/{}/{}/metrics/completions/leaders?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            urlencode(qs_params),
        )
    )

    return json.loads(response.read())


@api_error_protect
def get_course_details_completions_all_users(course_id):

    response = GET(
        '{}/{}/{}/metrics/completions/leaders?exclude_roles=none'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id
        )
    )

    return json.loads(response.read())


@api_error_protect
def get_course_details_metrics_grades_all_users(course_id, count):

    response = GET(
        '{}/{}/{}/metrics/grades/leaders?exclude_roles=none&count={}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            count
        )
    )

    return json.loads(response.read())


@api_error_protect
def get_course_details_metrics_all_users(course_id, organization_id=''):

    response = GET(
        '{}/{}/{}/metrics?metrics_required=users_completed,users_passed,avg_grade,avg_progress'
        '&organization={}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            organization_id
        )
    )

    return json.loads(response.read())


@api_error_protect
def get_course_details_metrics_filtered_by_groups(course_id, group_ids, organization_id = ''):

    response = GET(
        '{}/{}/{}/metrics/?metrics_required=users_completed&groups={}&organization={}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            group_ids,
            organization_id
        )
    )

    return json.loads(response.read())


@api_error_protect
def get_course_passed_users(course_id, page_num=1, page_size=100):
    """
    Returns paginated list of course passing users
    """
    qs_params = {
        "page_size": page_size,
        "page": page_num,
    }
    response = GET(
        '{}/{}/{}/users/passed?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            urlencode(qs_params)
        )
    )

    return JP.from_json(response.read(), user_models.UserListResponse)


@api_error_protect
def get_user_list_dictionary(course_id, program_id = None):
    return json.loads(get_user_list_json(course_id, program_id))


def parse_course_list_json_object(course_list_json_object):
    return CJP.from_json(json.dumps(course_list_json_object))

