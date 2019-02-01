from .common import DataManager
from lib.utils import DottableDict

from django.conf import settings

from main.models import CuratedContentItem
from courses.models import FeatureFlags, CourseMetaData

COURSE_PROPERTIES = DottableDict(
    CURATED_CONTENT='curated_content',
    DETAIL='detail',
    FEATURE_FLAG='feature_flag',
    GRADED_ITEMS_COUNT='graded_items_count',
    LANGUAGE='language',
    PREFETCHED_COURSE_OBJECT='prefetched_course_object',
    PREFETCHED_COURSE_OBJECT_STAFF='prefetched_course_object_staff',
    ROLES='roles',
    TABS='tabs',
    TAB_CONTENT='tabs_content',
    COURSE_META_DATA='course_meta_data',
    AVERAGE_SCORES='average_scores',
    TOTAL_LESSONS='total_lessons',
    TOTAL_STAFF_TOOLS='total_staff_tools',
)


class CourseDataManager(DataManager):
    cache_key_prefix = 'course'
    cache_expire_time = settings.CACHE_TIMEOUTS.get('course_data')

    def __init__(self, course_id):
        self.course_id = course_id
        self.cache_unique_identifier = self.course_id

    @property
    def total_lessons(self):
        return self.get_cached_data(property_name=COURSE_PROPERTIES.TOTAL_LESSONS)

    @total_lessons.setter
    def total_lessons(self, total_lessons):
        self.set_cached_data(COURSE_PROPERTIES.TOTAL_LESSONS, total_lessons)

    @property
    def total_staff_tools(self):
        return self.get_cached_data(property_name=COURSE_PROPERTIES.TOTAL_STAFF_TOOLS)

    @total_staff_tools.setter
    def total_staff_tools(self, total_staff_tools):
        self.set_cached_data(COURSE_PROPERTIES.TOTAL_STAFF_TOOLS, total_staff_tools)

    def get_curated_content_data(self):
        curated_content_data = self.get_cached_data(property_name=COURSE_PROPERTIES.CURATED_CONTENT)
        if curated_content_data is not None:
            return curated_content_data

        curated_content = CuratedContentItem.objects.filter(course_id=self.course_id).order_by('sequence')

        def filter_content_by_content_type(content_type):
            return [item for item in curated_content if item.content_type == content_type]

        articles = filter_content_by_content_type(CuratedContentItem.ARTICLE)[:3]
        videos = filter_content_by_content_type(CuratedContentItem.VIDEO)[:3]
        tweet = next(iter(filter_content_by_content_type(CuratedContentItem.TWEET)[:1]), None)
        quote = next(iter(filter_content_by_content_type(CuratedContentItem.QUOTE)[:1]), None)
        infographic = next(iter(filter_content_by_content_type(CuratedContentItem.IMAGE)[:1]), None)

        curated_content_data = dict(articles=articles, videos=videos, tweet=tweet, quote=quote, infographic=infographic)
        self.set_cached_data(
            property_name=COURSE_PROPERTIES.CURATED_CONTENT,
            data=curated_content_data
        )
        return curated_content_data

    def get_feature_flags(self):
        feature_flags = self.get_cached_data(property_name=COURSE_PROPERTIES.FEATURE_FLAG)
        if feature_flags is not None:
            return feature_flags

        feature_flags, created = FeatureFlags.objects.get_or_create(course_id=self.course_id)
        self.set_cached_data(
            property_name=COURSE_PROPERTIES.FEATURE_FLAG,
            data=feature_flags
        )
        return feature_flags

    def get_course_meta_data(self):
        course_meta_data = self.get_cached_data(property_name=COURSE_PROPERTIES.COURSE_META_DATA)
        if course_meta_data is not None:
            return course_meta_data

        course_meta_data, created = CourseMetaData.objects.get_or_create(course_id=self.course_id)

        self.set_cached_data(
            property_name=COURSE_PROPERTIES.COURSE_META_DATA,
            data=course_meta_data
        )
        return course_meta_data

    def get_language(self, user_id):
        language = self.get_cached_data(property_name=COURSE_PROPERTIES.LANGUAGE)
        if language is not None:
            return language

        from api_client import user_api
        course_detail = user_api.get_user_course_detail(user_id, self.course_id)
        language = course_detail.language.split('_')[0] if course_detail.language else None
        self.set_cached_data(
            property_name=COURSE_PROPERTIES.LANGUAGE, data=language,
            expiry_time=settings.CACHE_TIMEOUTS.get('course_language', settings.DEFAULT_CACHE_TIMEOUT)
        )
        return language

    def get_prefetched_course_object(self, user):
        cache_property = COURSE_PROPERTIES.PREFETCHED_COURSE_OBJECT

        if user:  # User may be an object or a dict.
            try:
                is_staff = user.is_staff
            except AttributeError:
                is_staff = user.get('is_staff')

            if is_staff:
                cache_property = COURSE_PROPERTIES.PREFETCHED_COURSE_OBJECT_STAFF

        return self.get_cached_data(cache_property)
