from django.db import models


class CuratedContentItem(models.Model):
    title = models.CharField(max_length=255, null=True)
    body = models.CharField(max_length=1000, null=True)
    byline = models.CharField(max_length=255, null=True)
    url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    
    TEXT = 'txt'
    VIDEO = 'vid'
    QUOTE = 'quo'
    TWEET = 'twt'
    ARTICLE = 'art'

    CONTENT_TYPES = (
        (TEXT, 'text'),
        (VIDEO, 'video'),
        (QUOTE, 'quote'),
        (TWEET, 'tweet'),
        (ARTICLE, 'article'),
    )
    content_type = models.CharField(max_length=3,
                                    choices=CONTENT_TYPES,
                                    default=TEXT)
    
    