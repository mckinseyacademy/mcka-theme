import httpretty
from urllib import urlencode

from django.conf import settings

from api_client.course_api import COURSE_COMPLETION_API, COURSEWARE_API


def setup_course_completions_response(course_id):
    course_path = '{}/'.format(course_id)
    api_params = {'page_size': 200}

    url = '{api_base}/{course_completion_api}/{course_path}?{params}'.format(
        api_base=settings.API_SERVER_ADDRESS,
        course_completion_api=COURSE_COMPLETION_API,
        course_path=course_path,
        params=urlencode(api_params),
    )

    httpretty.register_uri(
        httpretty.POST,
        url,
        body=course_completion_user,
        status=200,
        content_type='application/json',
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

    httpretty.register_uri(
        httpretty.GET,
        url,
        body=course_metrics_completions,
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
        body=course_metrics_grades,
        status=200,
        content_type='application/json',
    )


course_metrics_completions = '''{
    "total_users": 5,
    "total_possible_completions": 20,
    "course_avg": 4,
    "leaders": [
        {
            "id": 1,
            "username": "pro_tester",
            "title": "Mr",
            "profile_image": {
                "image_url_full": "http://localhost:8000/static/images/profiles/default_500.png",
                "image_url_large": "http://localhost:8000/static/images/profiles/default_120.png",
                "image_url_medium": "http://localhost:8000/static/images/profiles/default_50.png",
                "image_url_small": "http://localhost:8000/static/images/profiles/default_30.png",
                "has_image": false
            },
            "completions": 10
        },
        {
            "id": 2,
            "username": "pro_tester2",
            "title": "Mr",
            "profile_image": {
                "image_url_full": "http://localhost:8000/static/images/profiles/default_500.png",
                "image_url_large": "http://localhost:8000/static/images/profiles/default_120.png",
                "image_url_medium": "http://localhost:8000/static/images/profiles/default_50.png",
                "image_url_small": "http://localhost:8000/static/images/profiles/default_30.png",
                "has_image": false
            },
            "completions": 10
        }
    ]
}
'''


course_metrics_grades = '''{
    "user_grade": 0,
    "course_avg": 0.07
}'''


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
            }
        }
    ]
}'''
