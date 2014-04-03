''' Objects for courses built from json responses from API '''
from .json_object import JsonObject

# Create your models here.

# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods


class Page(JsonObject):

    ''' object representing a page / module within a subsection '''
    required_fields = ["id", "name", "uri", "modules", ]

    def vertical_usage_id(self):
        return self.id.replace('/', ';_')


class Sequential(JsonObject):

    ''' object representing a subsection within a chapter / lesson '''
    required_fields = ["id", "name", "uri", "modules", ]


class Chapter(JsonObject):

    ''' object representing a chapter / lesson within a course '''
    required_fields = ["id", "name", "uri", "modules", ]


class Course(JsonObject):

    ''' object representing a course '''
    required_fields = ["id", "name", "uri", "modules", ]
