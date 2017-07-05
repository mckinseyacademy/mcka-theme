"""
URLs for the certificates djangoapp.
"""
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^(?P<course_id>.*)/generate$', views.generate_course_certificates, name='generate_course_certificates'),
    url(r'^(?P<certificate_uuid>[0-9a-f]{32})$', views.get_certificate_by_uuid, name='get_certificate_by_uuid'),
    url(r'^template_assets/(?P<asset_id>\d+)/(?P<asset_name>.*)$', views.load_template_asset, name='load_template_asset'),
)
