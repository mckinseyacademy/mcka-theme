from .common import DataManager
from lib.utils import DottableDict

from django.conf import settings


GROUP_PROPERTIES = DottableDict(
    COURSES='courses',
)


class GroupDataManager(DataManager):
    cache_key_prefix = 'group'
    cache_expire_time = settings.CACHE_TIMEOUTS.get('group_data')

    def __init__(self, group_id):
        self.group_id = group_id
        self.cache_unique_identifier = self.group_id
