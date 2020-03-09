"""
URLs for the certificates djangoapp.
"""
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        r'^(?P<course_id>.*)/generate$',
        views.generate_course_certificates,
        name='generate_course_certificates'
    ),
    re_path(
        r'^(?P<certificate_uuid>[0-9a-f]{32})$',
        views.get_certificate_by_uuid,
        name='get_certificate_by_uuid'
    ),
    re_path(
        r'^template_assets/(?P<asset_id>\d+)/(?P<asset_name>.*)$',
        views.load_template_asset,
        name='load_template_asset'
    ),
]
