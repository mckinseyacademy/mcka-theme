import httpretty
from urllib import urlencode

from django.conf import settings

from api_client.course_api import COURSE_COMPLETION_API


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
