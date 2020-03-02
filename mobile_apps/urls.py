"""
URLs for the mobile app associations djangoapp.
"""
from django.urls import path

from . import views

urlpatterns = [
    path(
        'assetlinks.json',
        views.android_asset_links_file,
        name='android_asset_links_file'
    ),
    path(
        'apple-app-site-association',
        views.ios_site_association_file,
        name='ios_site_association_file'
    ),
]
