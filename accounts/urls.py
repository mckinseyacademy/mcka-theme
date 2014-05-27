from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('accounts',
    url(r'^user_profile.html$', views.user_profile, name='user_profile'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^activate/(?P<activation_code>.*)$', views.activate, name='activate'),
    url(r'^password/reset/$', views.reset, name='reset'),
	url(r'^password/reset/done/$', views.reset_done, name='reset_done'),
	url(r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', views.reset_confirm, name='reset_confirm'),
	url(r'^password/done/$', views.reset_complete, name='reset_complete'),
)
