from .common import DataManager
from lib.utils import DottableDict

from django.conf import settings


COURSE_PROPERTIES = DottableDict(
    DETAIL='detail',
    TABS='tabs',
    TAB_CONTENT='tabs_content'
)


class CourseDataManager(DataManager):
    cache_key_prefix = 'course'
    cache_expire_time = settings.CACHE_TIMEOUTS.get('course_data')

    def __init__(self, course_id):
        self.course_id = course_id
        self.cache_unique_identifier = self.course_id
