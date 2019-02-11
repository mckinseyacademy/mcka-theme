from django.dispatch import receiver
from django.db.models.signals import post_save

from courses.models import CourseMetaData, FeatureFlags

from api_data_manager.course_data import CourseDataManager, COURSE_PROPERTIES


@receiver(post_save, sender=CourseMetaData)
def delete_course_meta_data_cache(sender, instance, **kwargs):
    course_manager = CourseDataManager(instance.course_id)
    course_manager.delete_cached_data(COURSE_PROPERTIES.COURSE_META_DATA)


@receiver(post_save, sender=FeatureFlags)
def delete_feature_flags_cache(sender, instance, **kwargs):
    course_manager = CourseDataManager(instance.course_id)
    course_manager.delete_cached_data(COURSE_PROPERTIES.FEATURE_FLAG)
