from django.db import models
from json_object import JsonObject

import hashlib

# Create your models here.


class UserResponse(JsonObject):
    required_fields = ["email", "username"]

    def image_url(self, size=40):
        return "http://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower()).hexdigest() + "?s={}".format(size)

    def formatted_name(self):
        return "{} {}".format(self.first_name, self.last_name)


class AuthenticationResponse(JsonObject):
    required_fields = ['token', 'user']
    object_map = {
        "user": UserResponse
    }
