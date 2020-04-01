from django.contrib import sitemaps
from django.urls import reverse
import datetime


class Sitemap(sitemaps.Sitemap):
    def __init__(self, names):
        self.names = names

    def items(self):
        return self.names

    def changefreq(self, obj):
        return 'monthly'

    def lastmod(self, obj):
        return datetime.datetime.now()

    def location(self, obj):
        return reverse(obj)


class MarketingSitemap(sitemaps.Sitemap):
    def items(self):
        pages = [
            '/about/',
            '/programs/',
            '/experience/',
            '/contact/'
        ]
        return pages

    def changefreq(self, obj):
        return 'monthly'

    def lastmod(self, obj):
        return datetime.datetime.now()

    def location(self, obj):
        return obj
