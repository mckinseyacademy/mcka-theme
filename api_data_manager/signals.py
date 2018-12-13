from django.dispatch import Signal, receiver
from django.db.models.signals import post_save, post_delete

from main.models import CuratedContentItem
from courses.models import FeatureFlags, CourseMetaData

from .user_data import UserDataManager
from .group_data import GroupDataManager
from .course_data import CourseDataManager, COURSE_PROPERTIES
from .common_data import CommonDataManager

user_data_updated = Signal(providing_args=['user_ids', 'data_type'])
group_data_updated = Signal(providing_args=['group_ids', 'data_type'])
course_data_updated = Signal(providing_args=['course_ids', 'data_type'])
common_data_updated = Signal(providing_args=['data_type'])


@receiver(user_data_updated)
def user_data_updated_handler(sender, *args, **kwargs):
    user_ids = kwargs.get('user_ids')
    user_property = kwargs.get('data_type')

    for user_id in user_ids:
        data_manager = UserDataManager(user_id=user_id)
        data_manager.delete_cached_data(user_property)


@receiver(course_data_updated)
def course_data_updated_handler(sender, *args, **kwargs):
    course_ids = kwargs.get('course_ids')
    course_property = kwargs.get('data_type')

    for course_id in course_ids:
        data_manager = CourseDataManager(course_id=course_id)
        data_manager.delete_cached_data(course_property)


@receiver(group_data_updated)
def group_data_updated_handler(sender, *args, **kwargs):
    group_ids = kwargs.get('group_ids')
    user_property = kwargs.get('data_type')

    for group_id in group_ids:
        data_manager = GroupDataManager(group_id=group_id)
        data_manager.delete_cached_data(user_property)


@receiver(common_data_updated)
def common_data_updated_handler(sender, *args, **kwargs):
    common_data_property = kwargs.get('data_type')

    common_data_manager = CommonDataManager()
    common_data_manager.delete_cached_data(common_data_property)


@receiver([post_save, post_delete], sender=CuratedContentItem)
def delete_curated_content_cache(sender, instance, **kwargs):
    course_manager = CourseDataManager(instance.course_id)
    course_manager.delete_cached_data(COURSE_PROPERTIES.CURATED_CONTENT)


@receiver(post_save, sender=FeatureFlags)
def delete_feature_flags_cache(sender, instance, **kwargs):
    course_manager = CourseDataManager(instance.course_id)
    course_manager.delete_cached_data(COURSE_PROPERTIES.FEATURE_FLAG)


@receiver(post_save, sender=CourseMetaData)
def delete_course_meta_data_cache(sender, instance, **kwargs):
    course_manager = CourseDataManager(instance.course_id)
    course_manager.delete_cached_data(COURSE_PROPERTIES.COURSE_META_DATA)
