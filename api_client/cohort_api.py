import json
from urllib import urlencode

from django.conf import settings

from api_client import cohort_models, user_models, discussions_api
from api_client.api_error import api_error_protect
from api_client.json_object import JsonParser
from api_client.oauth2_requests import get_oauth2_session, get_and_unpaginate

COHORTS_SETTINGS_API = getattr(settings, 'COHORTS_SETTINGS_API', 'api/cohorts/v1/settings')
COHORTS_COURSES_API = getattr(settings, 'COHORTS_COURSES_API', 'api/cohorts/v1/courses')


@api_error_protect
def is_course_cohorted(course_id, edx_oauth2_session=None):
    """
    Return whether the course with given ``course_id``.
    """
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()
    url = '{}/{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        COHORTS_SETTINGS_API,
        course_id,
    )
    data = edx_oauth2_session.get(url).json()
    return data['is_cohorted']


@api_error_protect
def set_course_cohorted(course_id, is_cohorted, edx_oauth2_session=None):
    """
    Set whether the course with given ``course_id`` is cohorted.
    """
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()
    url = '{}/{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        COHORTS_SETTINGS_API,
        course_id,
    )
    if not is_cohorted:
        # Must disable before uncohorting
        discussions_api.set_divided_discussions(course_id, is_cohorted)
    data = edx_oauth2_session.put(
        url,
        data=json.dumps({'is_cohorted': is_cohorted})
    ).json()
    if is_cohorted:
        # Must enable after cohorting
        discussions_api.set_divided_discussions(course_id, is_cohorted)
    return data['is_cohorted']


@api_error_protect
def get_all_cohorts_for_course(course_id, edx_oauth2_session=None):
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()
    url = '{}/{}/{}/cohorts/'.format(
        settings.API_SERVER_ADDRESS,
        COHORTS_COURSES_API,
        course_id,
    )
    return edx_oauth2_session.get(url).json()


@api_error_protect
def get_cohort_for_course(course_id, cohort_id, edx_oauth2_session=None):
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()
    url = '{}/{}/{}/cohorts/{}'.format(
        settings.API_SERVER_ADDRESS,
        COHORTS_COURSES_API,
        course_id,
        cohort_id,
    )
    data = edx_oauth2_session.get(url).json()
    return JsonParser.from_dictionary(data, cohort_models.Cohort)


@api_error_protect
def update_cohort_for_course(
        course_id,
        cohort_id,
        name=None,
        assignment_type=None,
        edx_oauth2_session=None,
):
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()

    params = {}

    if name is not None:
        params['name'] = name

    if assignment_type is not None:
        params['assignment_type'] = assignment_type

    url = '{}/{}/{}/cohorts/{}'.format(
        settings.API_SERVER_ADDRESS,
        COHORTS_COURSES_API,
        course_id,
        cohort_id,
    )

    return edx_oauth2_session.patch(url, data=json.dumps(params))


@api_error_protect
def add_cohort_for_course(
        course_id,
        name,
        assignment_type,
        edx_oauth2_session=None,
):
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()

    params = json.dumps({
        'name': name,
        'assignment_type': assignment_type,
    })

    url = '{}/{}/{}/cohorts/'.format(
        settings.API_SERVER_ADDRESS,
        COHORTS_COURSES_API,
        course_id,
    )
    data = edx_oauth2_session.post(url, data=params).json()
    return data


@api_error_protect
def get_users_in_cohort(
        course_id,
        cohort_id,
        page_size=None,
        edx_oauth2_session=None,
):
    params = ''
    if page_size is not None:
        params = urlencode({'page_size': page_size})

    url = '{}/{}/{}/cohorts/{}/users/?{}'.format(
        settings.API_SERVER_ADDRESS,
        COHORTS_COURSES_API,
        course_id,
        cohort_id,
        params,
    )
    data = get_and_unpaginate(url)
    return [
        JsonParser.from_dictionary(user, user_models.UserResponse)
        for user in data
    ]


@api_error_protect
def add_user_to_cohort(
        course_id,
        cohort_id,
        username,
        edx_oauth2_session=None,
):
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()

    url = '{}/{}/{}/cohorts/{}/users/{}'.format(
        settings.API_SERVER_ADDRESS,
        COHORTS_COURSES_API,
        course_id,
        cohort_id,
        username,
    )
    data = edx_oauth2_session.post(url).json()
    return JsonParser.from_dictionary(data, cohort_models.CohortUserUpdateResponse)


@api_error_protect
def add_multiple_users_to_cohort(
        course_id,
        cohort_id,
        usernames,
        edx_oauth2_session=None,
):
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()

    url = '{}/{}/{}/cohorts/{}/users/'.format(
        settings.API_SERVER_ADDRESS,
        COHORTS_COURSES_API,
        course_id,
        cohort_id,
    )
    return edx_oauth2_session.post(url,data=json.dumps({'users': usernames})).json()


@api_error_protect
def remove_user_from_cohort(
        course_id,
        cohort_id,
        username,
        edx_oauth2_session=None,
):
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()

    url = '{}/{}/{}/cohorts/{}/users/{}'.format(
        settings.API_SERVER_ADDRESS,
        COHORTS_COURSES_API,
        course_id,
        cohort_id,
        username,
    )
    edx_oauth2_session.delete(url)


@api_error_protect
def import_users(course_id, data, edx_oauth2_session=None):
    """
    Return whether the course with given ``course_id``.
    """
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()
    url = '{}/{}/{}/users'.format(
        settings.API_SERVER_ADDRESS,
        COHORTS_COURSES_API,
        course_id,
    )
    return edx_oauth2_session.post(url, data=data).json()
