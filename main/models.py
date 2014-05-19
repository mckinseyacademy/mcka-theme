from django.db import models


class CuratedContentItem(models.Model):
    class Meta:
        db_table = 'curated_content_item'

    course_id = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255, null=True)
    body = models.CharField(max_length=1000, null=True)
    source = models.CharField(max_length=255, null=True)
    byline = models.CharField(max_length=255, null=True)
    byline_title = models.CharField(max_length=255, null=True)
    url = models.URLField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    twitter_username = models.CharField(max_length=255, null=True)
    sequence = models.IntegerField(null=False)
    created_at = models.DateTimeField(null=True)
    display_date = models.DateTimeField(null=True)

    TEXT = 'txt'
    VIDEO = 'vid'
    QUOTE = 'quo'
    TWEET = 'twt'
    ARTICLE = 'art'
    IMAGE = 'img'

    CONTENT_TYPES = (
        (TEXT, 'text'),
        (VIDEO, 'video'),
        (QUOTE, 'quote'),
        (TWEET, 'tweet'),
        (ARTICLE, 'article'),
        (IMAGE, 'img'),
    )
    content_type = models.CharField(max_length=3,
                                    choices=CONTENT_TYPES,
                                    default=TEXT)
