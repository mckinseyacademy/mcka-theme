''' Objects for users / authentication built from json responses from API '''
import hashlib

from .json_object import JsonObject


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


class UserCourse(JsonObject):
    required_fields = []


class UserList(JsonObject):
    object_map = {
        "users": UserResponse
    }
