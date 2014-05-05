from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('accounts',
    url(r'^user_profile.html$', views.user_profile, name='user_profile'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^activate/(?P<activation_code>.*)$', views.activate, name='activate'),
)
