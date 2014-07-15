''' Objects for users / authentication built from json responses from API '''
import hashlib

from .json_object import JsonObject


# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods,no-member


class UserResponse(JsonObject):

    ''' object representing a user from api json response '''
    required_fields = ["email", "username"]
    date_fields = ["created"]

    def image_url(self, size=40):
        ''' return default avatar unless the user has one '''
        # TODO: is the size param going to be used here?
        if hasattr(self, 'avatar_url') and self.avatar_url is not None:
            if size <= 40:
                return self.avatar_url[:-4] + '-40.jpg'
            elif size <= 120:
                return self.avatar_url[:-4] + '-120.jpg'
            else:
                return self.avatar_url
        else:
            return "/static/image/empty_avatar.png"

    @property
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

class UserList(JsonObject):
    object_map = {
        "users": UserResponse
    }

class UsersFiltered(JsonObject):
    object_map = {
        "results": UserResponse
    }
