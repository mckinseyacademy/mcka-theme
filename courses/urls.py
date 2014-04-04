from django.conf.urls import include, patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^(?P<course_id>.*)/lessons/(?P<chapter_id>.*)/module/(?P<page_id>.*)$', views.navigate_to_page, name='navigate_to_page'),
    url(r'^(?P<course_id>.*)/lessons/(?P<chapter_id>.*)$', views.infer_chapter_navigation, name='infer_chapter_navigation'),
    url(r'^(?P<course_id>.*)$', views.infer_course_navigation, name='infer_course_navigation'),
    url(r'^$', views.infer_default_navigation, name='infer_default_navigation'),
)
