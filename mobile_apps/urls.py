"""
URLs for the mobile app associations djangoapp.
"""
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(
        r'^assetlinks.json$',
        views.android_asset_links_file,
        name='android_asset_links_file'
    ),
    url(
        r'^apple-app-site-association$',
        views.ios_site_association_file,
        name='ios_site_association_file'
    ),
)
