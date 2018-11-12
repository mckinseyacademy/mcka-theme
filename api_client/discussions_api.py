import json

from django.conf import settings

from api_client.api_error import api_error_protect
from api_client.oauth2_requests import get_oauth2_session

DISCUSSION_ROLE_API = getattr(settings,
                              'DISCUSSION_TOPICS_API',
                              'api/discussion/v1/courses/{}/roles/{}')
DISCUSSION_SETTINGS_API = getattr(settings,
                                  'DISCUSSION_SETTINGS_API',
                                  'api/discussion/v1/courses/{}/settings')
DISCUSSION_TOPIC_API = getattr(settings,
                               'DISCUSSION_TOPICS_API',
                               'api/discussion/v1/course_topics/{}')


@api_error_protect
def get_all_topics_for_course(course_id, edx_oauth2_session=None):
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()
    url = '{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        DISCUSSION_TOPIC_API.format(course_id),
    )
    return edx_oauth2_session.get(url).json()


@api_error_protect
def set_divided_discussions(course_id, is_divided, edx_oauth2_session=None):
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()
    settings_url = '{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        DISCUSSION_SETTINGS_API.format(course_id),
    )
    headers = {
        'Content-Type': 'application/merge-patch+json'
    }
    data = json.dumps({'division_scheme': 'cohort' if is_divided else 'none'})
    edx_oauth2_session.patch(settings_url, data=data, headers=headers)

    if is_divided:
        # Get course-wide discussion topics
        topics_url = '{}/{}'.format(
            settings.API_SERVER_ADDRESS,
            DISCUSSION_TOPIC_API.format(course_id)
        )
        topics = edx_oauth2_session.get(topics_url).json()
        topic_ids = [v['id'] for v in topics.get('non_courseware_topics', [])]
        # Enable divided discussion in topics
        if topic_ids:
            data = json.dumps({"divided_course_wide_discussions": topic_ids})
            edx_oauth2_session.patch(settings_url, data=data, headers=headers)


@api_error_protect
def set_discussions_moderator(course_id, user_id, is_moderator, edx_oauth2_session=None):
    if not edx_oauth2_session:
        edx_oauth2_session = get_oauth2_session()
    url = '{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        DISCUSSION_ROLE_API.format(course_id, 'Moderator'),
    )
    from api_client import user_api
    user = user_api.get_user(user_id)
    data = {'user_id': user.username, 'action': 'allow' if is_moderator else 'revoke'}
    return edx_oauth2_session.post(url, json=data)


def add_discussion_moderator(course_id, user_id):
    return set_discussions_moderator(course_id, user_id, True)


def remove_discussion_moderator(course_id, user_id):
    return set_discussions_moderator(course_id, user_id, False)
