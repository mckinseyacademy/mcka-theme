from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'accounts.views.home', name='home'),
    url(r'^accounts/', include('accounts.urls'), name='accounts'),
    url(r'^courses/', include('courses.urls'), name='courses'),
)
