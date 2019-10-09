import json
import httpretty
from urllib.parse import urlencode

from django.conf import settings

from api_client.course_api import COURSE_COMPLETION_API, COURSEWARE_API


def setup_course_completions_response(course_id, username=None):
    course_path = '{}/'.format(course_id)
    api_params = {'page_size': 200}

    request_data = {}
    if username:
        request_data['username'] = username

    url = '{api_base}/{course_completion_api}/{course_path}?{params}'.format(
        api_base=settings.API_SERVER_ADDRESS,
        course_completion_api=COURSE_COMPLETION_API,
        course_path=course_path,
        params=urlencode(api_params),
    )

    httpretty.register_uri(
        httpretty.POST,
        url,
        json=request_data,
        body=course_completion_user,
        status=200,
        content_type='application/json',
    )


def setup_course_metrics_grades(course_id, **kwargs):
    qs_params = {"count": 3}
    qs_params.update(kwargs)

    url = '{}/{}/{}/metrics/grades/leaders?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params),
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(course_metrics_grades_leaders_list),
        status=200,
        content_type='application/json'
    )


def setup_course_metrics_completions(course_id, **kwargs):
    qs_params = {"count": 3}
    qs_params.update(kwargs)

    url = '{}/{}/{}/metrics/completions/leaders?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params),
    )
    if kwargs.get('skipleaders', None):
        course_metrics_completions_leaders_list['leaders'] = []

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(course_metrics_completions_leaders_list),
        status=200,
        content_type='application/json'
    )


def setup_get_course_metrics_leaders_response(course_id, **kwargs):
    qs_params = {}

    for key, value in list(kwargs.items()):
        if isinstance(value, list):
            qs_params[key] = ",".join(value)
        else:
            qs_params[key] = value

    url = '{}/{}/{}/metrics/leaders/?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params),
    )
    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(course_metrics_leaders_data),
        status=444 if kwargs.get('throw_error') else 200,
        content_type='application/json'
    )


def setup_course_metrics_social(course_id, count, throw_error, **kwargs):
    qs_params = {"count": count}
    qs_params.update(kwargs)

    httpretty.register_uri(
        httpretty.GET,
        '{}/{}/{}/metrics/social/leaders/?{}'.format(
            settings.API_SERVER_ADDRESS,
            COURSEWARE_API,
            course_id,
            urlencode(qs_params)
        ),
        body=json.dumps(course_metrics_social_leaders_list),
        status=444 if throw_error else 200,
        content_type='application/json'
    )


def setup_get_course_social_metrics_response(course_id, organization_id=None, scores=False):
    qs_params = {}
    if organization_id:
        qs_params['organization'] = organization_id
    if scores:
        qs_params['scores'] = scores

    url = '{}/{}/{}/metrics/social/?{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id,
        urlencode(qs_params)
    )

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=json.dumps(course_social_metrics),
        status=200,
        content_type='application/json'
    )


course_completion_user = '''{
    "pagination": {
        "count": 1,
        "previous": null,
        "num_pages": 1,
        "next": null
    },
    "results": [
        {
            "course_key": "CS101/ORG101/2018",
            "completion": {
                "earned": 3,
                "possible": 4,
                "percent": 0.75
            },
            "username": "mcka_admin_user"
        }
    ]
}'''

course_metrics_grades_leaders_list = {
    'course_avg': 6.873,
    'leaders': [
        {'id': 123, 'username': 'testuser1', 'title': 'Engineer',
         'profile_image_uploaded_at': '2014-01-15 06:27:54', 'grade': 0.92, 'created': '2014-01-15 06:27:54'},
        {'id': 983, 'username': 'testuser2', 'title': 'Analyst',
         'profile_image_uploaded_at': '2014-01-15 06:27:54', 'grade': 0.91, 'created': '2014-06-27 01:15:54'},
        {'id': 246, 'username': 'testuser3', 'title': 'Product Owner',
         'profile_image_uploaded_at': '2014-01-15 06:27:54', 'grade': 0.90, 'created': '2014-03-19 04:54:54'},
    ],
    'user_position': 4,
    'user_grade': 0.89,
}

course_metrics_completions_leaders_list = {
    "completions": 22,
    "course_avg": 7,
    "leaders": [
            {
                'id': 123,
                'username': 'testuser1',
                'title': 'Engineer',
                'profile_image_uploaded_at': '2014-01-15 06:27:54',
                'completions': 0.92
            },
            {
                'id': 983,
                'username': 'testuser2',
                'title': 'Analyst',
                'profile_image_uploaded_at': '2014-01-15 06:27:54',
                'completions': 0.91
            },
            {
                'id': 246,
                'username': 'testuser3',
                'title': 'Product Owner',
                'profile_image_uploaded_at': '2014-01-15 06:27:54',
                'completions': 0.90
            },
    ],
    "position": 4,
    "total_users": 116,
}

course_metrics_social_leaders_list = {
    "course_avg": 7,
    "leaders": [
        {'id': 123, 'username': 'testuser1', 'title': 'Engineer',
         'profile_image_uploaded_at': '2014-01-15 06:27:54', 'score': 80},
        {'id': 983, 'username': 'testuser2', 'title': 'Analyst',
         'profile_image_uploaded_at': '2014-01-15 06:27:54', 'score': 70},
        {'id': 246, 'username': 'testuser3', 'title': 'Product Owner',
         'profile_image_uploaded_at': '2014-01-15 06:27:54', 'score': 62},
    ],
    "position": 4,
    "score": 22,
}

course_metrics_leaders_data = {
    'grades': course_metrics_grades_leaders_list,
    'completions': course_metrics_completions_leaders_list,
    'social': course_metrics_social_leaders_list,
}

course_social_metrics = {
    "total_enrollments": 4,
    "users": {
        "2": {
            "num_threads": 1,
            "num_thread_followers": 0,
            "num_replies": 0,
            "num_flagged": 0,
            "num_comments": 0,
            "num_threads_read": 0,
            "num_downvotes": 0,
            "num_upvotes": 0,
            "num_comments_generated": 0
        },
        "8": {
            "num_threads": 1,
            "num_thread_followers": 0,
            "num_replies": 0,
            "num_flagged": 0,
            "num_comments": 0,
            "num_threads_read": 0,
            "num_downvotes": 0,
            "num_upvotes": 0,
            "num_comments_generated": 0
        }
    }
}
