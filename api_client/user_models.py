''' Objects for users / authentication built from json responses from API '''
import json
from urlparse import urljoin

from django.conf import settings

from .json_object import JsonObject, JsonObjectWithImage


# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods,no-member


class UserResponse(JsonObjectWithImage):

    ''' object representing a user from api json response '''
    required_fields = ["id", "email", "first_name", "username", "is_active"]
    date_fields = ["created"]

    def _get_profile_image_absolute_url(self, size_name):
        if self.profile_image.has_image and settings.DEBUG:
            return urljoin(
                settings.API_SERVER_ADDRESS,
                getattr(self.profile_image, size_name)
            )

        return getattr(self.profile_image, size_name)

    @property
    def image_url_full(self):
        return self._get_profile_image_absolute_url('image_url_full')

    @property
    def image_url_large(self):
        return self._get_profile_image_absolute_url('image_url_large')

    @property
    def image_url_medium(self):
        return self._get_profile_image_absolute_url('image_url_medium')

    @property
    def image_url_small(self):
        return self._get_profile_image_absolute_url('image_url_small')

    def get(self, attr):
        if hasattr(self, attr):
            return getattr(self, attr)
        return ''

    @property
    def formatted_name(self):
        ''' returns formatted name from first name and last name unless first name is defined'''
        if hasattr(self, "full_name"):
            return self.full_name

        return u"{} {}".format(self.first_name, self.last_name)

    def to_json(self):
        ''' return UserResponse object as json '''
        return json.dumps(self.to_dict())

    def to_dict(self):
        ''' return UserResponse object as dict '''
        unserializable_fields = ['uri', 'resources', 'created']
        user = {}
        for field, value in self.__dict__.iteritems():
            if field not in unserializable_fields:
                if field == 'profile_image':
                    user['image_url_full'] = self.image_url_full
                    user['image_url_large'] = self.image_url_large
                    user['image_url_medium'] = self.image_url_medium
                    user['image_url_small'] = self.image_url_small
                else:
                    user[field] = self.get(field)
        return user


class SimpleUserResponse(UserResponse):
    """
    Class representing a simple user response from api json response
    """
    required_fields = ["email", "username"]


class UserListResponse(JsonObject):
    object_map = {
        "results": UserResponse
    }


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
        "users": SimpleUserResponse
    }


class CityResponse(JsonObject):
    required_fields = ["city", "count"]


class CityList(JsonObject):
    object_map = {
        "results": CityResponse
    }


class UserSSOProviderAssociation(JsonObject):
    required_fields = ['provider_id', 'name']


class UserSSOProviderAssociationList(JsonObject):
    object_map = {
        'active': UserSSOProviderAssociation,
        'inactive': UserSSOProviderAssociation
    }
