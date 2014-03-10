from django.db import models
from json_object import JsonObject

# Create your models here.
class AuthenticationResponse(JsonObject):
    required_fields = ['session_key']

class UserResponse(JsonObject):
    required_fields = []