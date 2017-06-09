''' Objects for users / authentication built from json responses from API '''
import hashlib
import json

from .json_object import JsonObject, JsonObjectWithImage


# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods,no-member


class UserResponse(JsonObjectWithImage):

    ''' object representing a user from api json response '''
    required_fields = ["email", "username"]
    date_fields = ["created"]

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
                if field == 'avatar_url':
                    setattr(self, 'avatar_url', self.image_url(size=48))
                user[field] = self.get(field)
        return user


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
        "users": UserResponse
    }

class CityResponse(JsonObject):
    required_fields = ["city", "count"]

class CityList(JsonObject):
    object_map = {
        "results": CityResponse
    }


class UserSSOProviderAssociation(JsonObject):
    required_fields = ['provider_id', 'remote_id', 'name']


class UserSSOProviderAssociationList(JsonObject):
    object_map = {
        'active': UserSSOProviderAssociation,
        'inactive': UserSSOProviderAssociation
    }
