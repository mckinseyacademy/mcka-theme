from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^user_profile.html$', views.user_profile, name='user_profile'),
    url(r'^user_profile/image/edit$', views.user_profile_image_edit, name='user_profile_image_edit'),
    url(r'^edit_fullname/$', views.edit_fullname, name='edit_fullname'),
    url(r'^edit_title/$', views.edit_title, name='edit_title'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^activate/(?P<activation_code>.*)/(?P<registration>.*)/$', views.activate, name='activate'),
    url(r'^activate/(?P<activation_code>.*)$', views.activate, name='activate'),
    url(r'^activateV2/(?P<activation_code>.*)$', views.activate, name='activateV2'),
    url(r'^finalize/$', views.sso_finalize, name='sso_finalize'),
    url(r'^sso_launch/', views.sso_launch, name='sso_launch'),
    url(r'^sso_reg/$', views.sso_registration_form, name='sso_registration_form'),
    url(r'^sso_error/$', views.sso_error, name='sso_error'),
    url(r'^password/reset/done/$', views.reset_done, name='reset_done'),
    url(r'^password/reset/complete/$', views.reset_complete, name='reset_complete'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.reset_confirm, name='reset_confirm'),
    url(r'^password/reset/$', views.reset, name='reset'),
    url(r'^user/(?P<user_id>[0-9]+)/change_profile_image', views.change_profile_image, name='change_profile_image'),
    url(r'^images/(?P<image_url>.*)$', views.load_profile_image, name='load_profile_image'),
    url(
        r'^fill_email_and_redirect/(?P<redirect_url>.*)$',
        views.fill_email_and_redirect,
        name='fill_email_and_redirect'
    ),
    url(r'^api/access/(?P<access_key_code>.*)', views.get_access_key, name='access_key_data_api_view'),
]
