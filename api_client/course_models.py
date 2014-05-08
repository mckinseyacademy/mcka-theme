''' Objects for courses built from json responses from API '''
from .json_object import CategorisedJsonObject, JsonObject

# Create your models here.

# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods


class Page(CategorisedJsonObject):

    ''' object representing a page / module within a subsection '''
    required_fields = ["id", "name", ]

    def vertical_usage_id(self):
        return self.id.replace('/', ';_')


class Sequential(CategorisedJsonObject):

    ''' object representing a subsection within a chapter / lesson '''
    required_fields = ["id", "name", ]


class Chapter(CategorisedJsonObject):

    ''' object representing a chapter / lesson within a course '''
    required_fields = ["id", "name", ]


class Course(CategorisedJsonObject):

    ''' object representing a course '''
    required_fields = ["id", "name", ]


class CourseListCourse(JsonObject):
    required_fields = ["course_id", "display_name", ]


class CourseList(JsonObject):
    object_map = {
        "courses": CourseListCourse
    }

class CourseEnrollment(JsonObject):
    ''' object representing students/users enrolled to course '''
    required_fields = ["id", "email", "username",]

class CourseEnrollmentList(JsonObject):
    object_map = {
        "enrollments": CourseEnrollment
    }
