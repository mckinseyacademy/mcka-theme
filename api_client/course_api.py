''' API calls with respect to courses '''
from .json_object import CategorisedJsonParser
from .json_object import CategorisedJsonObject
from . import course_models
from .json_requests import GET
from urllib2 import HTTPError

from django.conf import settings

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

def get_course_list():
    '''
    Retrieves list of courses from openedx server
    '''
    response = GET('{}/{}'.format(
        settings.API_SERVER_ADDRESS,
        COURSEWARE_API)
    )
    return CJP.from_json(response.read())

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
    course.chapters = [module for module in course.modules if module.category == "chapter"]

    for chapter in course.chapters:
        chapter.sequentials = [module for module in chapter.modules if module.category == "sequential"]
        chapter.is_released = True

        for sequential in chapter.sequentials:
            sequential.pages = [module for module in sequential.modules if module.category == "vertical"]

    return course
