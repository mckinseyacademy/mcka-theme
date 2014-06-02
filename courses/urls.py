from django.conf.urls import include, patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^(?P<course_id>.*)/lessons/(?P<chapter_id>.*)/module/(?P<page_id>.*)$', views.navigate_to_lesson_module, name='navigate_to_lesson_module'),
    url(r'^(?P<course_id>.*)/overview$', views.course_overview, name='course_overview'),
    url(r'^(?P<course_id>.*)/news$', views.course_news, name='course_news'),
    url(r'^(?P<course_id>.*)/progress$', views.course_progress, name='course_progress'),
    url(r'^(?P<course_id>.*)/cohort$', views.course_cohort, name='course_cohort'),
    url(r'^(?P<course_id>.*)/syllabus$', views.course_syllabus, name='course_syllabus'),
    url(r'^(?P<course_id>.*)/resources$', views.course_resources, name='course_resources'),
    url(r'^(?P<course_id>.*)/group_work$', views.course_group_work, name='course_group_work'),
    url(r'^(?P<course_id>.*)/lessons/(?P<chapter_id>.*)$', views.infer_chapter_navigation, name='infer_chapter_navigation'),
    url(r'^(?P<course_id>.*)/lessons$', views.infer_course_navigation, name='infer_course_navigation'),
    url(r'^(?P<course_id>.*)/teaching_assistant$', views.contact_ta, name='contact_ta'),
    url(r'^(?P<course_id>.*)$', views.course_landing_page, name='course_landing_page'),
    url(r'^$', views.infer_default_navigation, name='infer_default_navigation'),
)
