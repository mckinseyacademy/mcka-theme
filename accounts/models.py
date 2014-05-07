'''
User model for use with remote authentication; must inherit from AbstractUser
Don't save in database, but we must inherit from AbstractUser (which in turn
inherits from model) and therefore tables get contructed
'''
from django.db import models
from django.contrib.auth.models import AbstractUser
from lib.authorization import is_user_in_group
from api_client.group_api import PERMISSION_GROUPS


class RemoteUser(AbstractUser):
    ''' user object that exists only in cache '''
    # TODO: replace with memcached on server
    temp_user_cache = {}
    _image_url = None

    session_key = models.CharField('session_key', max_length=255, unique=True)

    def update_response_fields(self, user_response, session_key=None):
        ''' take api response and blend the results into this user object '''
        if session_key is not None:
            self.session_key = session_key
        self.email = user_response.email
        self.username = user_response.username
        self.id = user_response.id
        self._image_url = user_response.image_url()

    def image_url(self):
        ''' get image utl for user '''
        return self._image_url

    #USERNAME_FIELD = "username"
    #REQUIRED_FIELDS = ["session_key"]

    def save(self, **kwargs):
        '''
        Notice we only update the cache, not the database
        The sourse of truth is the system we are talking to va the API
        '''
        RemoteUser.temp_user_cache[self.id] = self
        return True

    @staticmethod
    def cached_fetch(user_id):
        ''' get from cache if there '''
        if user_id in RemoteUser.temp_user_cache:
            return RemoteUser.temp_user_cache[user_id]
        return None

    @staticmethod
    def remove_from_cache(user_id):
        ''' clean from cache when tearing down session '''
        del RemoteUser.temp_user_cache[user_id]

#    def is_authenticated(self):
#        return True

#    def get_full_name(self):
#        return self.username

#    def get_short_name(self):
#        return self.username

    def is_mcka_admin(self):
        return is_user_in_group(self, PERMISSION_GROUPS.MCKA_ADMIN)

    def is_mcka_subadmin(self):
        return is_user_in_group(self, PERMISSION_GROUPS.MCKA_SUBADMIN)

    def is_client_admin(self):
        return is_user_in_group(self, PERMISSION_GROUPS.CLIENT_ADMIN)

    def is_client_subadmin(self):
        return is_user_in_group(self, PERMISSION_GROUPS.CLIENT_SUBADMIN)

    def is_mcka_ta(self):
        return is_user_in_group(self, PERMISSION_GROUPS.MCKA_TA)

    def is_client_ta(self):
        return is_user_in_group(self, PERMISSION_GROUPS.CLIENT_TA)


# class AprosUser(RemoteUser):
#     def set_user_attributes(self, user):
#         for k, v in user.__dict__:
#             setattr(self, k, v)

#     def is_mcka_admin():
#         return True

#     def is_mcka_subadmin():
#         return True

#     def is_client_admin():
#         return True

#     def is_client_subadmin():
#         return True

#     def is_mcka_ta():
#         return True

#     def is_client_ta():
#         return True
