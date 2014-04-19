''' Objects for users / authentication built from json responses from API '''
from .json_object import JsonObject

import hashlib
import datetime


# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods,no-member


class UserResponse(JsonObject):
    ''' object representing a user from api json response '''
    required_fields = ["email", "username"]

    def image_url(self, size=40):
        ''' returns gravatar image based on user's email '''
        # double-size and shrink so that these look good on retina displays
        return "http://www.gravatar.com/avatar/{}?s={}".format(
            hashlib.md5(self.email.lower()).hexdigest(),
            size * 2
        )

    def formatted_name(self):
        ''' returns formatted name from first name and last name '''
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

class UserProgram(JsonObject):
    ''' object representing a users's program from api json response '''
    required_fields = ["id"]


# TODO UserStatus removed for now until bookmarking available
# class UserStatus(JsonObject):
#     ''' object representing a user's status from api json response '''
#     required_fields = []
#     object_map = {
#         "courses": UserCourse,
#         "programs": UserProgram,
#     }

#     def get_bookmark_for_course(self, course_id):
#         ''' returns bookmark for specific course if present '''
#         for course_status in self.courses:
#             if course_status.id == course_id and hasattr(course_status, 'bookmark'):
#                 return course_status.bookmark

#         return None

class UserCourse(JsonObject):
    required_fields = []

class Group(JsonObject):
    ''' object representing a group of which a user can be a member '''
    required_fields = ['id', 'name']
