import debug_toolbar
from django.conf.urls import patterns, include, url
from django.conf.urls import handler404
from django.conf.urls import handler500
from django.conf import settings
from django.views.i18n import javascript_catalog

from main import views
from sitemap import *
from admin import views as adminviews
from courses import views as courseviews
from accounts import views as accountsviews


urlpatterns = patterns(
    '',
    url(r'^$', 'accounts.views.home', name='home'),
    url(r'^home$', 'accounts.views.protected_home', name='protected_home'),
    url(r'^login$', 'accounts.views.login', name='login'),
    url(r'^terms/', 'main.views.terms', name='terms'),
    url(r'^privacy/', 'main.views.privacy', name='privacy'),
    url(r'^faq/', 'main.views.faq', name='faq'),
    url(r'^error_404/', 'main.views.error_404', name='error_404'),
    url(r'^error_500/', 'main.views.error_500', name='error_500'),
    url(r'^accounts/', include('accounts.urls'), name='accounts'),
    url(r'^courses/', include('courses.urls'), name='courses'),
    url(r'^certificates/', include('certificates.urls'), name='certificates'),
    url(r'^admin/', include('admin.urls'), name='admin'),
    url(r'^heartbeat$', include('heartbeat.urls'), name='heartbeat'),
    url(r'^.well-known/', include('mobile_apps.urls'), name='mobile_apps'),
    url(r'^mcka-api/v1/', include('public_api.urls'), name='public_api'),
    url(r'^api/', include('edx_notifications.server.api.urls_mock')),
    url(r'^notification_redir$', 'main.views.notification_redir'),
    url(r'^access/(?P<code>[^/]*)$', 'accounts.views.access_key', name="access_key"),
    url(r'^__debug__/', include(debug_toolbar.urls)),
    url(r'^registration/(?P<course_run_name>.+)/$', accountsviews.demo_registration, name='demo_registration'),
    url(r'^manifest.json/(?P<user_id>\d+)/$', 'main.views.android_manifest_json', name='android_manifest_json'),
    url(r'^jsi18n/$', javascript_catalog, name='javascript-catalog'),
)

if settings.DEBUG:
    urlpatterns += (url(r'^update_language$', views.PreviewLanguageView.as_view(), name='preview_language'),)

urlpatterns += patterns(
    '',
    url(r'^learnerdashboard/(?P<learner_dashboard_id>[0-9]+)$', courseviews.course_learner_dashboard, name='course_learner_dashboard'),
    url(r'^learnerdashboard/bookmark_lesson/(?P<learner_dashboard_id>[0-9]+)/', courseviews.course_learner_dashboard_bookmark_lesson, name='course_learner_dashboard_bookmark_lesson'),
    url(r'^learnerdashboard/bookmark_tile/(?P<learner_dashboard_id>[0-9]+)/', courseviews.course_learner_dashboard_bookmark_tile, name='course_learner_dashboard_bookmark_tile'),
    url(r'^learnerdashboard/courses/(?P<course_id>.*)/lessons/(?P<chapter_id>.*)/module/(?P<page_id>.*)/(?P<tile_type>.*)/(?P<tile_id>.*)/(?P<learner_dashboard_id>[0-9]+)$', courseviews.navigate_to_lesson_module, name='navigate_to_lesson_module'),
    url(r'^learnerdashboard/(?P<learner_dashboard_id>[0-9]+)/courses/(?P<course_id>.*)/resources$', courseviews.course_resources_learner_dashboard, name='course_resources_learner_dashboard'),
    url(r'^learnerdashboard/(?P<learner_dashboard_id>[0-9]+)/courses/(?P<course_id>.*)/discussion', courseviews.course_discussion_learner_dashboard, name='course_discussion_learner_dashboard'),
    url(r'^learnerdashboard/(?P<learner_dashboard_id>[0-9]+)/courses/(?P<course_id>.*)/group_work/(?P<workgroup_id>[0-9]+)$', courseviews.workgroup_course_group_work, name='user_course_group_work_learner_dashboard'),
    url(r'^learnerdashboard/(?P<learner_dashboard_id>[0-9]+)/courses/(?P<course_id>.*)/group_work$', courseviews.user_course_group_work_learner_dashboard, name='user_course_group_work_learner_dashboard'),
    url(r'^learnerdashboard/(?P<learner_dashboard_id>[0-9]+)/calendar$', courseviews.course_learner_dashboard_calendar, name='course_learner_dashboard_calendar'),
)

urlpatterns += patterns(
    '',
    url(r'^company_images/(?P<image_url>.*)$', adminviews.load_background_image, name='load_background_image'),
)

if settings.RUN_LOCAL_MOCK_API:
    urlpatterns += patterns('', url(r'^mockapi/', include('mockapi.urls'), name='mockapi'),)

sitemaps = {
    'pages': Sitemap(['home', 'terms', 'privacy', 'faq']),
    'marketing': MarketingSitemap,
}

urlpatterns += patterns('',
    (r'^sitemap\.xml', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

urlpatterns += patterns(
    '',
    url(r'^', include('marketing.urls'), name='marketing'),
)

urlpatterns += patterns(
    '',
    url(r'^company_images/(?P<image_url>.*)$', adminviews.load_background_image, name='load_background_image'),
)

handler404 = views.error_404
handler500 = views.error_500
