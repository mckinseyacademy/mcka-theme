''' Objects for users / authentication built from json responses from API '''
import hashlib

from django.conf import settings

from .json_object import JsonObject


# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods,no-member


class UserResponse(JsonObject):

    ''' object representing a user from api json response '''
    required_fields = ["email", "username"]

    def image_url(self, size=40, path='relative'):
        ''' return default avatar unless the user has one '''
        # TODO: is the size param going to be used here?
        if hasattr(self, 'avatar_url') and self.avatar_url is not None:
            if size <= 40:
                image_url = self.avatar_url[:-4] + '-40.jpg'
            elif size <= 120:
                image_url = self.avatar_url[:-4] + '-120.jpg'
            else:
                image_url = self.avatar_url

            if path == 'absolute' and settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto.S3BotoStorage':
                from django.core.files.storage import default_storage
                image_url = default_storage.url(
                    self._strip_proxy_image_url(image_url))
        else:
            image_url = "/static/image/empty_avatar.png"
        return image_url

    def _strip_proxy_image_url(self, profileImageUrl):
        if profileImageUrl[:10] == '/accounts/':
            image_url = profileImageUrl[10:]
        else:
            image_url = profileImageUrl
        return image_url

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


class UserCourse(JsonObject):
    required_fields = []


class UserList(JsonObject):
    object_map = {
        "users": UserResponse
    }

class UsersFiltered(JsonObject):
    object_map = {
        "results": UserResponse
    }
