from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^$', 'accounts.views.home', name='home'),
    url(r'^accounts/', include('accounts.urls'), name='accounts'),
    url(r'^courses/', include('courses.urls'), name='courses'),
    url(r'^admin/', include('admin.urls'), name='admin'),
)
