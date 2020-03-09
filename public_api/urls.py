from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'token/?', views.api_create_token, name='api_token'),
    re_path(r'^courses/(?P<course_id>.*)$', views.course, name='api_course'),
    re_path(r'^user/?$', views.user_course, name='api_user_course'),
    re_path(r'^users/?$', views.users, name='api_users'),
    re_path(r'^reset_password/?$', views.reset_password, name='api_reset_password'),
    path(
        'feature_flag_custom_taxonomy',
        views.get_course_feature_flag_and_custom_taxonomy,
        name='get_course_feature_flag_and_custom_taxonomy'
    ),
    re_path(
        r'^(?P<course_id>.*)/feature_flag_custom_taxonomy$',
        views.get_course_feature_flag_and_custom_taxonomy,
        name='get_course_feature_flag_and_custom_taxonomy'
    ),
    path(
        'feature_flag', views.get_course_feature_flag,
        name='get_course_feature_flag'
    ),
    re_path(
        r'^(?P<course_id>.*)/feature_flag$',
        views.get_course_feature_flag,
        name='get_course_feature_flag'
    ),
    re_path(
        r'^send_activation_link/(?P<login_id>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})',
        views.send_participant_activation_link,
        name='send_participant_activation_link'
    ),
]
