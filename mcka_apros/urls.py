import debug_toolbar
from django.conf.urls import handler404
from django.conf.urls import handler500
from django.conf import settings
from django.views.i18n import JavaScriptCatalog
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.urls import path, re_path, include

from main import views as main_views
from .sitemap import *  # noqa: F403 TODO replace star imports with named imports
from admin import views as adminviews
from courses import views as courseviews
from accounts import views as accountsviews

urlpatterns = [
    path('', accountsviews.home, name='home'),
    path('home', accountsviews.home, name='protected_home'),
    path('login', accountsviews.home, name='login'),
    path('terms/', main_views.terms, name='terms'),
    path('privacy/', main_views.privacy, name='privacy'),
    path('faq/', main_views.faq, name='faq'),
    path('getting-started/', main_views.getting_started, name='getting_started'),
    path('error_404/', main_views.error_404, name='error_404'),
    path('error_500/', main_views.error_500, name='error_500'),
    path('accounts/', include('accounts.urls'), name='accounts'),
    path('courses/', include('courses.urls'), name='courses'),
    path('certificates/', include('certificates.urls'), name='certificates'),
    path('admin/', include('admin.urls'), name='admin'),
    path('heartbeat', include('heartbeat.urls'), name='heartbeat'),
    path('.well-known/', include('mobile_apps.urls'), name='mobile_apps'),
    path('mcka-api/v1/', include('public_api.urls'), name='public_api'),
    path('api/', include('edx_notifications.server.api.urls_mock')),
    path('notification_redir', main_views.notification_redir),
    re_path(r'^access/(?P<code>[^/]*)$', accountsviews.access_key, name="access_key"),
    path('__debug__/', include(debug_toolbar.urls)),
    re_path(r'^registration/(?P<course_run_name>.+)/$', accountsviews.demo_registration, name='demo_registration'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    re_path(r'^storage/(?P<path>.*)', main_views.private_storage_access, name='private_storage'),
    path(
        'language_switch',
        accountsviews.switch_language_based_on_preference, name='language_switcher'
    ),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicons/favicon.ico')), name="favicon")
]

if settings.DEBUG:
    urlpatterns.extend([path('update_language', main_views.PreviewLanguageView.as_view(), name='preview_language')])

urlpatterns.extend([
    path(
        'learnerdashboard/<int:learner_dashboard_id>',
        courseviews.course_learner_dashboard,
        name='course_learner_dashboard'
    ),
    path(
        'learnerdashboard/bookmark_lesson/<int:learner_dashboard_id>/',
        courseviews.course_learner_dashboard_bookmark_lesson,
        name='course_learner_dashboard_bookmark_lesson'
    ),
    path(
        'learnerdashboard/bookmark_tile/<int:learner_dashboard_id>/',
        courseviews.course_learner_dashboard_bookmark_tile,
        name='course_learner_dashboard_bookmark_tile'
    ),
    re_path(
        r'^learnerdashboard/courses/(?P<course_id>.*)/lessons/(?P<chapter_id>.*)/module/(?P<page_id>.*)/'
        r'(?P<tile_type>.*)/(?P<tile_id>.*)/(?P<learner_dashboard_id>[0-9]+)$',
        courseviews.navigate_to_lesson_module,
        name='navigate_to_lesson_module'
    ),
    re_path(
        r'^learnerdashboard/(?P<learner_dashboard_id>[0-9]+)/courses/(?P<course_id>.*)/resources$',
        courseviews.course_resources_learner_dashboard,
        name='course_resources_learner_dashboard'
    ),
    re_path(
        r'^learnerdashboard/(?P<learner_dashboard_id>[0-9]+)/courses/(?P<course_id>.*)/discussion',
        courseviews.course_discussion_learner_dashboard,
        name='course_discussion_learner_dashboard'
    ),
    re_path(
        r'^learnerdashboard/(?P<learner_dashboard_id>[0-9]+)/courses/(?P<course_id>.*)/group_work/'
        r'(?P<workgroup_id>[0-9]+)$',
        courseviews.workgroup_course_group_work,
        name='workgroup_course_group_work'
    ),
    re_path(
        r'^learnerdashboard/(?P<learner_dashboard_id>[0-9]+)/courses/(?P<course_id>.*)/group_work$',
        courseviews.user_course_group_work_learner_dashboard,
        name='user_course_group_work_learner_dashboard'
    ),
    path(
        'learnerdashboard/<int:learner_dashboard_id>/calendar',
        courseviews.course_learner_dashboard_calendar,
        name='course_learner_dashboard_calendar'
    )
])

urlpatterns.extend([
    re_path(
        r'^company_images/(?P<image_url>.*)$', adminviews.load_background_image, name='load_background_image'
    )
])

if settings.RUN_LOCAL_MOCK_API:
    urlpatterns.extend([
        path('mockapi/', include('mockapi.urls'), name='mockapi')
    ])

sitemaps = {
    'pages': Sitemap(['home', 'terms', 'privacy', 'faq']),  # noqa: F405 TODO import Sitemap and dont use star imports
    'marketing': MarketingSitemap,  # noqa: F405 TODO import MarketingSitemap and dont use star imports
}

urlpatterns.extend([
    re_path(r'^sitemap\.xml', sitemap, {'sitemaps': sitemaps})
])

urlpatterns.extend([
    path('', include('marketing.urls'), name='marketing')
])

urlpatterns.extend([
    re_path(r'^company_images/(?P<image_url>.*)$', adminviews.load_background_image, name='load_background_image')
])

handler403 = main_views.error_403
handler404 = main_views.error_404  # noqa: F811 TODO fix issue ----> redefinition of unused 'handler404' from line 3
handler500 = main_views.error_500  # noqa: F811 TODO fix issue ----> redefinition of unused 'handler500' from line 4
