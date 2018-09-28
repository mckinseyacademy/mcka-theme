from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'token/?', views.api_create_token, name='api_token'),
    url(r'^courses/(?P<course_id>.*)$', views.course, name='api_course'),
    url(r'^user/?$', views.user_course, name='api_user_course'),
    url(r'^users/?$', views.users, name='api_users'),
    url(r'^reset_password/?$', views.reset_password, name='api_reset_password'),
    url(r'^feature_flag$', views.get_feature_flag_mobile, name='get_feature_flag_mobile'),
    url(r'^(?P<course_id>.*)/feature_flag$', views.get_feature_flag_mobile, name='get_feature_flag_mobile'),
]
