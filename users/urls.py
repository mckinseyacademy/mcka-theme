from django.conf.urls import include, patterns, url

from users import views

urlpatterns = patterns('users',
    url(r'^user_profile.html$', views.user_profile, name='user_profile'),
)
