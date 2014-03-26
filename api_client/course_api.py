from json_object import JsonParser as JP, JsonObject
import course_models
from json_requests import GET, POST, DELETE, PUT

from django.conf import settings

COURSEWARE_API = 'api/courses'


def get_course(course_id):
    response = GET('{}/{}/{}'.format(settings.API_SERVER_ADDRESS, COURSEWARE_API, course_id))
    return JP.from_json(response.read(), course_models.Course)


def get_page_content(page_content_id):
    response = GET('{}/{}/page_content/{}'.format(settings.API_SERVER_ADDRESS, COURSEWARE_API, page_content_id))
    return JP.from_json(response.read(), course_models.PageContent)
