from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from api_data_manager.course_data import CourseDataManager, COURSE_PROPERTIES
from main.models import CuratedContentItem


@receiver([post_save, post_delete], sender=CuratedContentItem)
def delete_curated_content_cache(sender, instance, **kwargs):
    course_manager = CourseDataManager(instance.course_id)
    course_manager.delete_cached_data(COURSE_PROPERTIES.CURATED_CONTENT)
