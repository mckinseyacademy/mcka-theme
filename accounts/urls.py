from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('accounts',
    url(r'^user_profile.html$', views.user_profile, name='user_profile'),
    url(r'^user_profile/image/edit$', views.user_profile_image_edit, name='user_profile_image_edit'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^activate/(?P<activation_code>.*)$', views.activate, name='activate'),
	url(r'^password/reset/done/$', views.reset_done, name='reset_done'),
    url(r'^password/reset/complete/$', views.reset_complete, name='reset_complete'),
	url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.reset_confirm, name='reset_confirm'),
    url(r'^password/reset/$', views.reset, name='reset'),
)
