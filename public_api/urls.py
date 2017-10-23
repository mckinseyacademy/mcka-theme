from django.conf.urls import include, patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'token/?', views.api_create_token, name='api_token'),
    url(r'^courses/(?P<course_id>.*)$', views.course, name='api_course'),
    url(r'^user/?$', views.user_course, name='api_user_course'),
    url(r'^users/?$', views.users, name='api_users'),
    url(r'^reset_password/?$', views.reset_password, name='api_reset_password'),
)
