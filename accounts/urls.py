from django.urls import path, re_path

from . import views

urlpatterns = [
    path('user_profile.html', views.user_profile, name='user_profile'),
    path('user_profile/image/edit', views.user_profile_image_edit, name='user_profile_image_edit'),
    path('edit_fullname/', views.edit_fullname, name='edit_fullname'),
    path('edit_title/', views.edit_title, name='edit_title'),
    path('login/', views.home, name='login'),
    path('logout/', views.logout, name='logout'),
    re_path(r'^activate/(?P<activation_code>.*)/(?P<registration>.*)/$', views.activate, name='activate'),
    re_path(r'^activate/(?P<activation_code>.*)$', views.activate, name='activate'),
    re_path(r'^activateV2/(?P<activation_code>.*)$', views.activate, name='activateV2'),
    path('finalize/', views.sso_finalize, name='sso_finalize'),
    path('sso_launch/', views.sso_launch, name='sso_launch'),
    path('sso_reg/', views.sso_registration_form, name='sso_registration_form'),
    path('sso_error/', views.sso_error, name='sso_error'),
    path('password/reset/done/', views.reset_done, name='reset_done'),
    path('password/reset/complete/', views.reset_complete, name='reset_complete'),
    re_path(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.reset_confirm, name='reset_confirm'),
    re_path(r'^password/reset/$', views.reset, name='reset'),
    re_path(r'^user/(?P<user_id>[0-9]+)/change_profile_image', views.change_profile_image, name='change_profile_image'),
    re_path(r'^images/(?P<image_url>.*)$', views.load_profile_image, name='load_profile_image'),
    re_path(
        r'^fill_email_and_redirect/(?P<redirect_url>.*)$',
        views.fill_email_and_redirect,
        name='fill_email_and_redirect'
    ),
    re_path(r'^api/access/(?P<access_key_code>.*)', views.get_access_key, name='access_key_data_api_view'),
    path('refresh_user_session', views.refresh_user_session, name='refresh_user_session'),
    path('new-ui-visited/', views.new_ui_visited, name='new_ui_visited'),
]
