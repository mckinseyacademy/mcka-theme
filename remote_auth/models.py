from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser
import json_backend

# Create your models here.
class RemoteUser(AbstractUser):
    session_key = models.CharField('session_key', max_length = 2000, unique = True)
    #username = models.CharField('username', max_length = 255, unique = True)

    def update_from_auth_response(self, auth_response):
        self.session_key = auth_response.token
        self.email = auth_response.user.email
        self.username = auth_response.user.username
        self.id = auth_response.user.id

    #USERNAME_FIELD = "username"
    #REQUIRED_FIELDS = ["session_key"]

    def save(self, **kwargs):
        return True

#    def is_authenticated(self):
#        return True

#    def get_full_name(self):
#        return self.username

#    def get_short_name(self):
#        return self.username
