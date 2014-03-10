from django.db import models
from json_object import JsonObject

import hashlib

# Create your models here.
class AuthenticationResponse(JsonObject):
    required_fields = ['session_key', 'user_id']

class UserResponse(JsonObject):
    required_fields = ["email", "name", "username"]

    def image_url(self, size = 40):
        return "http://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower()).hexdigest() + "?s={}".format(size) 
