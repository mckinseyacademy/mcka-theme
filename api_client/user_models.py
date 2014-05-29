''' Objects for users / authentication built from json responses from API '''
import hashlib

from .json_object import JsonObject
from .json_object import DataOnly, JsonObject, CategorisedJsonObject


# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods,no-member


class UserResponse(JsonObject):

    ''' object representing a user from api json response '''
    required_fields = ["email", "username"]

    def image_url(self, size=40):
        ''' return default avatar unless the user has one '''
        # TODO: is the size param going to be used here?
        return "/static/image/empty_avatar.png"

    def formatted_name(self):
        ''' returns formatted name from first name and last name unless first name is defined'''
        if hasattr(self, "full_name"):
            return self.full_name

        return "{} {}".format(self.first_name, self.last_name)


class AuthenticationResponse(JsonObject):

    ''' object representing an authenticated session from api json response '''
    required_fields = ['token', 'user']
    object_map = {
        "user": UserResponse
    }


class UserCourseStatus(JsonObject):

    ''' object representing a user's course status from api json response '''
    required_fields = ["position"]


class UserCourse(JsonObject):
    required_fields = []


class UserList(JsonObject):
    object_map = {
        "users": UserResponse
    }


class CourseSectionSummary(JsonObject):
    object_map = {
        "section_total": DataOnly,
        "scores": DataOnly,
    }


class GradeSummary(JsonObject):
    object_map = {
        "section_breakdown": CategorisedJsonObject,
        "totaled_scores": DataOnly,
        "grade_breakdown": CategorisedJsonObject
    }


class CourseSummary(JsonObject):
    object_map = {
        "sections": CourseSectionSummary
    }


class CourseGrades(JsonObject):
    object_map = {
        "courseware_summary": CourseSummary,
        "grade_summary": GradeSummary
    }
