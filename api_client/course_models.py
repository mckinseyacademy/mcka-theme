''' Objects for courses built from json responses from API '''
from api_client.json_object import JsonObject

# Create your models here.

# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods

class Page(JsonObject):
    ''' object representing a page / module within a chapter / lesson'''
    required_fields = []

class Chapter(JsonObject):
    ''' object representing a chapter / lesson within a course '''
    required_fields = []
    object_map = {
        "pages" : Page,
    }

class Course(JsonObject):
    ''' object representing a course '''
    required_fields = []
    object_map = {
        "chapters" : Chapter,
    }

class PageContent(JsonObject):
    ''' object for loading page content from the API server '''
    required_fields = []
