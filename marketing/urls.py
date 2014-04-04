from django.conf.urls import include, patterns, url

from marketing import views

urlpatterns = patterns('',
    url(r'^(?P<page_name>.*)$', views.infer_default_navigation, name='infer_default_navigation'),
)
