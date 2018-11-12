from django.db import models
from django.utils.translation import ugettext_lazy as _

class CuratedContentItem(models.Model):
    class Meta:
        db_table = 'curated_content_item'
        index_together = [
            ('course_id', 'content_type')
        ]

    course_id = models.CharField(max_length=255, null=False)
    title = models.CharField(max_length=255, blank=True, default='')
    body = models.CharField(max_length=1000, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    byline = models.CharField(max_length=255, blank=True, null=True)
    byline_title = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(blank=True, default='')
    thumbnail_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    twitter_username = models.CharField(max_length=255, blank=True, null=True)
    sequence = models.IntegerField(null=False, db_index=True)
    created_at = models.DateTimeField(null=True, blank=True)
    display_date = models.DateTimeField(null=True, blank=True)

    TEXT = 'txt'
    VIDEO = 'vid'
    QUOTE = 'quo'
    TWEET = 'twt'
    ARTICLE = 'art'
    IMAGE = 'img'

    CONTENT_TYPES = (
        (TEXT, _('text')),
        (VIDEO, _('video')),
        (QUOTE, _('quote')),
        (TWEET, _('tweet')),
        (ARTICLE, _('article')),
        (IMAGE, _('img')),
    )
    content_type = models.CharField(max_length=3,
                                    choices=CONTENT_TYPES,
                                    default=TEXT)
