from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'mcka_apros.views.home', name='home'),
    url(r'^login/', 'mcka_apros.views.login', name='login'),
    url(r'^foundation/', include('foundation.urls'), name='foundation'),
)
