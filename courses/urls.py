from django.conf.urls import include, patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^(?P<course_id>.*)/lessons/(?P<chapter_id>.*)/module/(?P<page_id>.*)$', views.navigate_to_lesson_module, name='navigate_to_lesson_module'),
    url(r'^(?P<course_id>.*)/view/(?P<current_view>\w+)$', views.navigate_to_page, name='navigate_to_page'),
    url(r'^(?P<course_id>.*)/lessons/(?P<chapter_id>.*)$', views.infer_chapter_navigation, name='infer_chapter_navigation'),
    url(r'^(?P<course_id>.*)/lessons$', views.infer_course_navigation, name='infer_course_navigation'),
    url(r'^(?P<course_id>.*)/teaching_assistant$', views.contact_ta, name='contact_ta'),
    url(r'^(?P<course_id>.*)/group_email/(?P<group_id>.*)$', views.contact_group, name='contact_group'),
    url(r'^$', views.infer_default_navigation, name='infer_default_navigation'),
    url(r'^(?P<course_id>.*)$', views.navigate_to_page, name='navigate_to_page'),
)
