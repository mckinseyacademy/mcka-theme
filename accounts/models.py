'''
User model for use with remote authentication; must inherit from AbstractUser
Don't save in database, but we must inherit from AbstractUser (which in turn
inherits from model) and therefore tables get contructed
'''
import hashlib
import random
from datetime import datetime, timedelta
from django.db import models as db_models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from lib.authorization import is_user_in_permission_group
from api_client.group_api import PERMISSION_GROUPS
from admin.models import CourseRun

from django.utils.functional import cached_property
from django.core.cache import cache
from api_client import user_api


class RemoteUser(AbstractUser):
    ''' user object that exists only in cache '''
    avatar_url = None
    avatar_url_absolute = None

    session_key = db_models.CharField('session_key', max_length=255, unique=True)

    def update_response_fields(self, user_response, session_key=None):
        ''' take API response and blend the results into this user object '''
        if session_key is not None:
            self.session_key = session_key
        self.email = user_response.email
        self.username = user_response.username
        self.id = user_response.id
        self.avatar_url = user_response.image_url()
        self.avatar_url_relative = user_response.image_url(path='relative')
        self.is_staff = user_response.is_staff

    def image_url(self):
        ''' get image URL for user '''
        return self.avatar_url

    #USERNAME_FIELD = "username"
    #REQUIRED_FIELDS = ["session_key"]

    def save(self, **kwargs):
        '''
        Notice we only update the cache, not the database
        The source of truth is the system we are talking to via the API
        '''
        cache.set('user_' + str(self.id), self)
        return True

    def get_roles(self):
        ''' Return user roles list '''
        return user_api.get_user_roles(self.id)

    def get_roles_on_course(self, course_id):
        roles = self.get_roles()
        return [role for role in roles if role.course_id == course_id]

    @staticmethod
    def cached_fetch(user_id):
        ''' get user from cache if there '''
        return cache.get('user_' + str(user_id), None)

    @staticmethod
    def remove_from_cache(user_id):
        ''' remove user from cache when tearing down session '''
        cache.delete('user_' + str(user_id))

#    def is_authenticated(self):
#        return True

#    def get_full_name(self):
#        return self.username

#    def get_short_name(self):
#        return self.username

    @cached_property
    def is_mcka_admin(self):
        return is_user_in_permission_group(self, PERMISSION_GROUPS.MCKA_ADMIN)

    @cached_property
    def is_mcka_subadmin(self):
        return is_user_in_permission_group(self, PERMISSION_GROUPS.MCKA_SUBADMIN)

    @cached_property
    def is_client_admin(self):
        return is_user_in_permission_group(self, PERMISSION_GROUPS.CLIENT_ADMIN)

    @cached_property
    def is_company_admin(self):
        return is_user_in_permission_group(self, PERMISSION_GROUPS.COMPANY_ADMIN)

    @cached_property
    def is_client_subadmin(self):
        return is_user_in_permission_group(self, PERMISSION_GROUPS.CLIENT_SUBADMIN)

    @cached_property
    def is_mcka_ta(self):
        return is_user_in_permission_group(self, PERMISSION_GROUPS.MCKA_TA)

    @cached_property
    def is_client_ta(self):
        return is_user_in_permission_group(self, PERMISSION_GROUPS.CLIENT_TA)

    @cached_property
    def is_internal_admin(self):
        return is_user_in_permission_group(self, PERMISSION_GROUPS.INTERNAL_ADMIN)


class UserActivation(db_models.Model):
    user_id = db_models.IntegerField(unique=True)
    activation_key = db_models.CharField(max_length=40, unique=True, db_index=True)
    task_key = db_models.CharField(max_length=40, db_index=True, default='')
    first_name = db_models.CharField(max_length=40, default='N/A')
    last_name = db_models.CharField(max_length=40, default='N/A')
    email = db_models.EmailField(default='N/A')
    company_id = db_models.IntegerField(default=0)

    @staticmethod
    def generate_activation_key(email):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        return hashlib.sha1(salt+email).hexdigest()

    @classmethod
    def user_activation(cls, user):
        activation_record = cls.objects.create(user_id=user.id, activation_key=cls.generate_activation_key(user.email))
        activation_record.save()

        return activation_record

    @classmethod
    def get_user_activation(cls, user):
        activation_records = cls.objects.filter(user_id=user.id)

        if len(activation_records) > 0:
            return activation_records[0]

        return None

    @classmethod
    def user_activation_by_task_key(cls, user, task_key, company_id):
        activation_record = cls.objects.create(user_id=user.id, activation_key=cls.generate_activation_key(user.email), task_key=task_key, 
            first_name=user.first_name, last_name=user.last_name, email=user.email, company_id=company_id)
        activation_record.save()
        return activation_record

    @classmethod
    def get_activations_by_task_key(cls, task_key):
        activation_records = cls.objects.filter(task_key=task_key)
        return activation_records


class UserPasswordReset(db_models.Model):
    user_id = db_models.IntegerField(unique=True)
    validation_key = db_models.CharField(max_length=40, unique=True, db_index=True)
    time_requested = db_models.DateTimeField(default=datetime.now)

    @staticmethod
    def generate_validation_key(email):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        return hashlib.sha1(salt+email).hexdigest()

    @classmethod
    def create_record(cls, user):
        validation_record = cls.get_user_validation_record(user)
        if validation_record is not None:
            validation_record.delete()
        reset_record = cls.objects.create(user_id=user.id, validation_key=cls.generate_validation_key(user.email))
        reset_record.save()

        return reset_record

    @classmethod
    def get_user_validation_record(cls, user):
        reset_record = cls.objects.filter(user_id=user.id)

        if len(reset_record) > 0:
            return reset_record[0]

        return None

    @classmethod
    def check_user_validation_record(cls, user, token, current_time):
        reset_record = cls.get_user_validation_record(user)
        if reset_record is not None:
            if reset_record.validation_key == token and (reset_record.time_requested + timedelta(days=1)) >= timezone.now():
                return reset_record
        return None

class PublicRegistrationRequest(db_models.Model):

    first_name = db_models.CharField(blank=False, null=False, max_length=50)
    last_name = db_models.CharField(blank=False, null=False, max_length=50)
    company_name = db_models.CharField(blank=False, null=False, max_length=50)
    company_email = db_models.EmailField(blank=False, null=False, unique=True)
    current_role = db_models.CharField(blank=False, null=True, max_length=100)
    current_role_other = db_models.CharField(blank=True, null=True, max_length=60)

    mcka_user = db_models.BooleanField()
    new_user = db_models.BooleanField()

    course_run = db_models.ForeignKey(
        CourseRun,
        on_delete=db_models.CASCADE,
    )
