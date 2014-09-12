from django.conf.urls import include, patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^styleguide/$', views.styleguide, name='styleguide'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^(?P<page_name>.*)/$', views.infer_default_navigation, name='infer_default_navigation'),
)
