''' API calls with respect to courses '''
from api_client.json_object import JsonParser as JP
from api_client import course_models
from api_client.json_requests import GET

from django.conf import settings

COURSEWARE_API = 'api/courses'

def get_course(course_id):
    '''
    Retrieves course structure information from the API for specified course
    '''
    response = GET('{}/{}/{}'.format(
        # TODO: remove forced MOCK reference when real API becomes available
        settings.API_MOCK_SERVER_ADDRESS,
        COURSEWARE_API,
        course_id)
    )
    return JP.from_json(response.read(), course_models.Course)


def get_page_content(page_content_id):
    '''
    Retrieves specific page content including xblock
    '''
    response = GET('{}/{}/page_content/{}'.format(
        # TODO: remove forced MOCK reference when real API becomes available
        settings.API_MOCK_SERVER_ADDRESS,
        COURSEWARE_API,
        page_content_id)
    )
    return JP.from_json(response.read(), course_models.PageContent)
