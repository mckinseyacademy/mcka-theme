from django.db import models
from django.contrib.auth.models import AbstractUser  # , AbstractBaseUser
import json_backend

# Create your models here.


class RemoteUser(AbstractUser):
    # TODO: replace with memcached on server
    temp_user_cache = {}

    session_key = models.CharField('session_key', max_length=2000, unique=True)
    #username = models.CharField('username', max_length = 255, unique = True)

    def update_response_fields(self, user_response, session_key=None):
        if session_key != None:
            self.session_key = session_key
        self.email = user_response.email
        self.username = user_response.username
        self.id = user_response.id
        self._image_url = user_response.image_url()

    def image_url(self):
        return self._image_url

    #USERNAME_FIELD = "username"
    #REQUIRED_FIELDS = ["session_key"]

    def save(self, **kwargs):
        RemoteUser.temp_user_cache[self.id] = self
        return True

    @staticmethod
    def cached_fetch(user_id):
        if user_id in RemoteUser.temp_user_cache:
            return RemoteUser.temp_user_cache[user_id]
        return None

    @staticmethod
    def remove_from_cache(user_id):
        del RemoteUser.temp_user_cache[user_id]

#    def is_authenticated(self):
#        return True

#    def get_full_name(self):
#        return self.username

#    def get_short_name(self):
#        return self.username
