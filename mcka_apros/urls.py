from django.conf.urls import patterns, include, url
from django.conf.urls import handler404
from django.conf.urls import handler500
from django.conf import settings
from main import views

urlpatterns = patterns(
    '',
    url(r'^$', 'accounts.views.home', name='home'),
    url(r'^terms/', 'main.views.terms', name='terms'),
    url(r'^privacy/', 'main.views.privacy', name='privacy'),
    url(r'^faq/', 'main.views.faq', name='faq'),
    url(r'^error_404/', 'main.views.error_404', name='error_404'),
    url(r'^error_500/', 'main.views.error_500', name='error_500'),
    url(r'^accounts/', include('accounts.urls'), name='accounts'),
    url(r'^courses/', include('courses.urls'), name='courses'),
    url(r'^admin/', include('admin.urls'), name='admin'),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

if settings.RUN_LOCAL_MOCK_API:
    urlpatterns += patterns('', url(r'^mockapi/', include('mockapi.urls'), name='mockapi'),)

urlpatterns += patterns(
    '',
    url(r'^(?P<page_name>.*)/$', include('marketing.urls'), name='marketing'),
)

handler404 = views.error_404
handler500 = views.error_500
