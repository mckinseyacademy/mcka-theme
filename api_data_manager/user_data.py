import json

from django.core.cache import cache

from .common import DataManager
from lib.util import DottableDict

from django.conf import settings

USER_PROPERTIES = DottableDict(
    PREFERENCES='preferences',
    PROFILE='profile',
    GROUPS='groups',
    ORGANIZATIONS='organizations',
    COURSES='courses',
)

GROUPS_SUB_TYPES = DottableDict(
    SERIES='series',
    PERMISSIONS='permission',
    REVIEW_ASSIGNMENTS='reviewassignment'
)


class UserDataManager(DataManager):
    cache_key_prefix = 'user'
    cache_expire_time = settings.CACHE_TIMEOUTS.get('user_data')

    def __init__(self, user_id, identifiers=[]):
        self.user_id = user_id
        self.cache_unique_identifier = '{}_{}'.format('_'.join(identifiers), user_id) \
            if identifiers else user_id

    def delete_cached_data(self, property_name):

        if property_name == USER_PROPERTIES.GROUPS:
            # need to delete user course programs records as well
            user_courses = self.get_cached_data(property_name=USER_PROPERTIES.COURSES)
            if user_courses is not None:
                user_courses = json.loads(user_courses)
                group_name = GROUPS_SUB_TYPES.SERIES

                for course in user_courses:
                    cache_key = self.get_cache_key(
                        property_name='{}_{}'.format(property_name, group_name),
                        identifier='{}_{}'.format(course.get('id'), self.user_id)
                    )
                    cache.delete(cache_key)

            for group_key, group_name in GROUPS_SUB_TYPES.iteritems():
                cache_key = self.get_cache_key(property_name='{}_{}'.format(property_name, group_name))
                cache.delete(cache_key)

        super(UserDataManager, self).delete_cached_data(property_name)
