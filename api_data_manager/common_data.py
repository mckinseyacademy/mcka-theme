from .common import DataManager
from lib.utils import DottableDict

from django.conf import settings


COMMON_DATA_PROPERTIES = DottableDict(
    PROGRAM_COURSES_MAPPING='program_courses_mapping',
    COMPANION_APP_COURSES='companion_app_courses',
    PERMISSION_GROUPS='permission_groups',
)


class CommonDataManager(DataManager):
    cache_key_prefix = 'common'
    cache_expire_time = settings.CACHE_TIMEOUTS.get('common_data')
    cache_unique_identifier = 'common'
