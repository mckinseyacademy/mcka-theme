import logging

from django.core.management.base import BaseCommand
from django.db.models import Q

from main.models import CuratedContentItem

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Updates the curated content urls to https'

    def handle(self, *args, **options):
        items = CuratedContentItem.objects.filter(
            Q(url__contains='http://') |
            Q(thumbnail_url__contains='http://') |
            Q(image_url__contains='http://')
        )

        for item in items:
            logger.info('Course id: {} Updating urls: {} {} {}'.format(
                item.course_id,
                item.url,
                item.thumbnail_url,
                item.image_url
            ))
            if item.url is not None:
                item.url = item.url.replace('http://', 'https://')
            if item.thumbnail_url is not None:
                item.thumbnail_url = item.thumbnail_url.replace('http://', 'https://')
            if item.image_url is not None:
                item.image_url = item.image_url.replace('http://', 'https://')
            item.save()
