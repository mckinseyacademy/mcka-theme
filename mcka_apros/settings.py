#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Django settings for academy project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import datetime
import os
from logsettings import get_logger_config

from kombu import Queue, Exchange


from django.utils.translation import ugettext_lazy as _


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1x@epyq-))w6z8a@_9f+c8%g#n8o75jeh8c8d4_&y+f@2_(des'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ASSETS_SOURCE_ROOT = 'static'
ASSETS_SOURCE_ROOT_V2 = 'static_v2'

LOGGING = get_logger_config(BASE_DIR,
                            logging_env="dev",
                            tracking_filename="tracking.log",
                            dev_env=True,
                            debug=True)

ALLOWED_HOSTS = []

# Application definition
AUTH_USER_MODEL = 'accounts.RemoteUser'

DEFAULT_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
)

THIRD_PARTY_APPS = (
    'debug_toolbar',
    'django_assets',
    'djcelery',
    'rest_framework',
    # additional release utilities to ease automation
    'release_util',
    # Django Waffle for feature-flipping
    'waffle',
)

LOCAL_APPS = (
    'api_client',
    'accounts',
    'assets',
    'debug_remote_calls',
    'main',
    'courses',
    'admin',
    'marketing',
    'license',
    'heartbeat',
    'public_api',
    'certificates',
    'mobile_apps',
    'api_data_manager',
    'manager_dashboard',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# explicitly add 'debug_toolbar.middleware.DebugToolbarMiddleware',
# otherwise this doesn't seem to appear on AWS environments
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'accounts.middleware.session_timeout.SessionTimeout',
    'accounts.middleware.thread_local.ThreadLocal',
    'main.middleware.allow_embed_url.AllowEmbedUrlMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'courses.middleware.apros_platform_language.AprosPlatformLanguage',
    'accounts.middleware.ajax_redirect.AjaxRedirect',
    'lib.middleware.handle_prior_ids.PriorIdRequest',
    'waffle.middleware.WaffleMiddleware',
)

ROOT_URLCONF = 'mcka_apros.urls'

ALLOW_EMBED_URL = ''

WSGI_APPLICATION = 'mcka_apros.wsgi.application'

AUTHENTICATION_BACKENDS = (
    # 'django.contrib.auth.backends.ModelBackend',
    'accounts.json_backend.JsonBackend',
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mcka_apros',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    },
    'edx': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'edx',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', u'English'),
    ('ar', u'العربية'),  # Arabic
    ('es', u'Español'),
    ('nl', u'Dutch'),
    ('pt', u'Português'),
    ('zh', u'中文(简体)'),
    ('fr', u'Français'),
    ('ja', u'日本人'),
    ('de', u'Deutsch'),
)


USE_I18N = True
USE_L10N = True
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

USE_TZ = True
TIME_ZONE = 'UTC'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_cache')
MEDIA_ROOT = ''
ASSETS_ROOT = 'static/'
ASSETS_ROOT_V2 = 'static_v2/'
ASSETS_MANIFEST = False
ASSETS_CACHE = False
ASSETS_MODULES = [
    'assets.assets',
    'assets.assets_v2',
]
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "static/gen"),
    os.path.join(BASE_DIR, "static_v2"),
)

BASE_CERTIFICATE_TEMPLATE_ASSET_PATH = 'certificates/template_assets/'

# Handle session is not Json Serializable
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# We want a different name for cookies than on the LMS to allow to set
# the LMS cookies at the domain level from apros
SESSION_COOKIE_NAME = 'apros_sessionid'
CSRF_COOKIE_NAME = 'apros_csrftoken'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_TIMEOUT_SECONDS = 300
SESSION_COOKIE_AGE = 2592000

# 30 Days for react native apps
MOBILE_APP_SESSION_TIMEOUT_SECONDS = 2592000
MOBILE_APP_USER_AGENT = "com.mcka.RNApp"

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# LMS
LMS_BASE_DOMAIN = 'mckinseyacademy.com'
LMS_SUB_DOMAIN = 'lms'
LMS_PORT = None
LMS_SESSION_COOKIE_DOMAIN = None  # Default: use current/same domain
# LMS_AUTH_URL: relative or absolute URL to the LMS's /auth/ urls, used for SSO.
# Normally this is on the same domain as Apros and is forwarded to the LMS by an nginx reverse proxy rule
LMS_AUTH_URL = '/auth/'

NO_PROGRAM_NAME = _("McKinsey Management Program")
GROUP_PROJECT_IDENTIFIER = "GROUP_PROJECT_"

DISCUSSION_IDENTIFIER = "DISCUSSION_"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'global-cache',
        'TIMEOUT': 3600,
    }
}

# Api address
# API_SERVER_ADDRESS = 'http://localhost:8000'
API_SERVER_ADDRESS = 'http://openedxapi.apiary-mock.com'
STUDIO_SERVER_ADDRESS = ''
API_MOCK_SERVER_ADDRESS = 'http://openedxapi.apiary-mock.com'

RUN_LOCAL_MOCK_API = False
LOCAL_MOCK_API_FILES = [
    os.path.join(BASE_DIR, 'edx-solutions-apiary.apib'),
    os.path.join(BASE_DIR, 'mock_supplementals.apib'),
]

# EdX Api Key
# Set this on OpenEdx server, and within production environment to whichever value is desired
EDX_API_KEY = 'test_api_key'

# OAuth2 Client Credentials
# * These are the values for client_id and client_secret defined in the LMS in
#   /admin/oauth2_provider/application/
# * The application should have a visibility of "confidential"
# * The application should use the "Client Credentials" workflow.
# * The application should be belong to a user with `staff` access. (Preferably
#   one that's only used for oauth connections).
# * These values can be overridden to the appropriate value in local_settings.py.
OAUTH2_OPENEDX_CLIENT_ID = 'open'
OAUTH2_OPENEDX_CLIENT_SECRET = 'sesame'

# edX LMS shared secret used to validate provider data during SSO logins
EDX_SSO_DATA_HMAC_KEY = '1private_apros_key'

# When autoprovisioning (see previous setting), set the user's city to this value. (A city is
# required for things like the map of students, but we don't get 'city' from the SSO provider.)
SSO_AUTOPROVISION_CITY = "New York"

# Mobile app settings

# OAuth2 Credentials for Mobile
# * These are the values for client_id and client_secret defined in the LMS in
#   /admin/oauth2/client/
# * The client should have "Client type" of "Confidential (Web applications)"
# * The client should added as a trusted client in the LMS at
#   /admin/edx_oauth2_provider/trustedclient/
# * The redirect uri should be "{APROS_BASE_URL}/accounts/finalize/"
# * These values can be overridden to the appropriate value in local_settings.py.
OAUTH2_MOBILE_CLIENT_ID = 'responsible'
OAUTH2_MOBILE_CLIENT_SECRET = 'silk'

# The path to the endpoint on the mobile scheme where the mobile auth
# credentials or error message is to be sent. e.g. mcka://sso/?access_token=...
MOBILE_SSO_PATH = 'sso/'

################################################################################

# Whether or not to cache courseware content locally, defult=False but can be overridden in local_settings.py
USE_SESSION_COURSEWARE_CACHING = False

# Google Analytics Tracking ID
GA_TRACKING_ID = None  # should be UA-48573128-1 for McKA production

# While we have TA email group, define it here
TA_EMAIL_GROUP = 'tas@mckinseyacademy.com'
INITIAL_PASSWORD = 'PassworD12!@'

# Email address students get their enrollment email sent from
ENROLL_STUDENT_EMAIL = 'support@mckinseyacademy.com'

# Mcka support email
MCKA_SUPPORT_EMAIL = 'support@mckinseyacademy.com'

# Disabling automatic program enrollment for no (MCKIN-1750)
ENABLE_AUTOMATIC_EMAILS_UPON_PROGRAM_ENROLLMENT = False

# EMAIL BACKEND

APROS_EMAIL_SENDER = "no-reply@mckinseyacademy.com"

MCKINSEY_EMAIL_DOMAIN = "@mckinsey.com"

CERTIFICATES_EMAIL_SUBJECT = _("Congratulations! Your certificate has been generated")

# Date formatting rules
DATE_DISPLAY_FORMAT = "%B %d, %Y"
SHORT_DATE_FORMAT = "%m/%d/%Y"

# Points for social activities
SOCIAL_METRIC_POINTS = {
    'num_threads': 10,
    'num_comments': 15,
    'num_replies': 15,
    'num_upvotes': 25,
    'num_thread_followers': 5,
    'num_comments_generated': 15,
}

ADMINISTRATIVE_COMPANY = 'mckinsey_and_company'

API_SERVER_PREFIX = '/'.join(['api', 'server'])

# CELERY SETTINGS
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
# Important: we allow pickle serialization so that large CSV files can easily be transferred
# for async processing, but pickle serialization should *only* be used for such files
# that are validated and handed to us by Django first. Do not use pickle under any other
# circumstances, because it opens doors to remote code execution.
CELERY_ACCEPT_CONTENT = ['json', 'pickle']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
BROKER_TRANSPORT_OPTIONS = {'confirm_publish': True}
CELERYD_PREFETCH_MULTIPLIER = 1  # Each worker should only fetch one message at a time

CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('high_priority', Exchange('high_priority'), routing_key='high_priority'),
)

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_CREATE_MISSING_QUEUES = True
CELERY_TIMEZONE = 'UTC'

# Api locations
COURSEWARE_API = '/'.join([API_SERVER_PREFIX, 'courses'])
GROUP_API = '/'.join([API_SERVER_PREFIX, 'groups'])
ORGANIZATION_API = '/'.join([API_SERVER_PREFIX, 'organizations'])
PROJECT_API = '/'.join([API_SERVER_PREFIX, 'projects'])
AUTH_API = '/'.join([API_SERVER_PREFIX, 'sessions'])
USER_API = '/'.join([API_SERVER_PREFIX, 'users'])
WORKGROUP_API = '/'.join([API_SERVER_PREFIX, 'workgroups'])
MOBILE_APP_API = '/'.join([API_SERVER_PREFIX, 'mobileapps'])
MANAGER_API = '/'.join(['api', 'user_manager', 'v1'])
COURSE_ENROLLMENT_API = '/'.join(['api', 'enrollment', 'v1', 'enrollments'])
COURSE_COMPLETION_API = os.path.join('api', 'completion-aggregator', 'v1', 'course')
COURSE_COURSE_API = os.path.join('api', 'courses', 'v1', 'courses')
COURSE_BLOCK_API = os.path.join('api', 'courses', 'v1', 'blocks')
COURSE_COHORTS_API = '/'.join(['api', 'cohorts', 'v1'])

# set AWS querystring authentication to false
AWS_QUERYSTRING_AUTH = False

# Components whose contents do not count towards progress calculation
PROGRESS_IGNORE_COMPONENTS = [
    'discussion-course',
    'group-project',
    'discussion-forum',
    'discussion',

    # GP v2 categories
    'gp-v2-project',
    'gp-v2-activity',
    'gp-v2-stage-basic',
    'gp-v2-stage-completion',
    'gp-v2-stage-submission',
    'gp-v2-stage-team-evaluation',
    'gp-v2-stage-peer-review',
    'gp-v2-stage-evaluation-display',
    'gp-v2-stage-grade-display',
    'gp-v2-resource',
    'gp-v2-video-resource',
    'gp-v2-submission',
    'gp-v2-peer-selector',
    'gp-v2-group-selector',
    'gp-v2-review-question',
    'gp-v2-peer-assessment',
    'gp-v2-group-assessment',
    'gp-v2-static-submissions',
    'gp-v2-static-grade-rubric',
    'gp-v2-project-team',
    'gp-v2-navigator',
    'gp-v2-navigator-navigation',
    'gp-v2-navigator-resources',
    'gp-v2-navigator-submissions',
    'gp-v2-navigator-ask-ta',
    'gp-v2-navigator-private-discussion',
]

# roles which should neither updated nor deleted while updating other roles
IGNORE_ROLES = [
    'instructor',
    'staff',
]

# Zendesk Settings
ZENDESK_API = {
    'username': 'pam@mckinseyacademy.com',
    'token': 'uiXVhEjOO2Os7NxUUBQvMZvsqBGDqfUJBPC8PAsG',
    'subdomain': 'mckinseyacademy',
}

# Mailchimp Settings
MAILCHIMP_API = {
    'dc': 'us3',
    'key': 'a619ba3dfa632c8984c96f6ec254aa4a-us3',
    'stay_informed_list_id': 'd61ad96c25',
}

# progress bar chart colours
PROGRESS_BAR_COLORS = {
    "normal": "#b1c2cc",  # $mckinsey-academy-blue-gray
    "dropped": "#e5ebee",  # $mckinsey-academy-bright-gray
    "group_work": "#66a5b5",  # $mckinsey-academy-turquoise
    "total": "#e37222",  # $mckinsey-orange
    "proforma": "none",
}

COMPANY_GENERATE_IMAGE_SIZES = [[140, 40], [175, 50]]
# remove any of these sizes while regenerating the changed images
PROFILE_REMOVE_IMAGE_SIZES = [40, 120]
COMPANY_REMOVE_IMAGE_SIZES = [40, 120, 80, 160]

TEMP_IMAGE_FOLDER = "profile_temp_images/"

FEATURES = {
    'notes': False,
    # ADMIN COURSES SECTION
    'ADMIN_COURSES_TAB': False,
    # ADMIN PARTICIPANTS SECTION
    'ADMIN_PARTICIPANTS_TAB': False,
    # ADMIN COMPANIES SECTION
    'ADMIN_COMPANIES_TAB': False,
}

# LEARNER DASHBOARD FEATURE ON/OFF SETTING
LEARNER_DASHBOARD_ENABLED = False

LOGIN_BUTTON_FOR_MOBILE_ENABLED = True

# NOTIFICATION IN CASE THE NUMBER OF PARTICIPANTS IS CLOSE TO MAX
COURSE_RUN_PARTICIPANTS_TRESHOLD = 4000
DEDICATED_COURSE_RUN_PERSON = "staff@mckinseyacademy.com"

TEMPLATE_NEW_DIRS = [os.path.join(BASE_DIR, 'templates_v2')]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'lib.context_processors.user_program_data',
                'lib.context_processors.settings_data',
                'lib.context_processors.mobile_login_data',
                'lib.context_processors.set_mobile_app_id',
            ],
            'loaders': [
                ('mcka_apros.templates_loaders.CachedLoader', [
                    'mcka_apros.templates_loaders.CustomHamlPyFilesystemLoader',
                    'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ])
            ]
        },
    },
]

# Data retrieval settings
MAX_USERS_PER_PAGE = 250

# Heap Analytics Env ID
HEAP_ENV_ID = ''

# Waffle switches
COHORT_FLAG_NAMESPACE = 'course_groups'
COHORT_FLAG_SWITCH_NAME = 'enable_apros_integration'

DELETION_FLAG_NAMESPACE = 'data_deletion'
DELETION_FLAG_SWITCH_NAME = 'enable_data_deletion'

DELETION_SYNCHRONOUS_MAX_USERS = 50

try:
    from local_settings import *  # noqa: F403, F401
except ImportError:
    pass

# Include any apps added from switch set in local_settings
if RUN_LOCAL_MOCK_API:
    INSTALLED_APPS += (
        'mockapi',
    )

DEFAULT_DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
)

LOCAL_DEBUG_TOOLBAR_PANELS = (
    'debug_remote_calls.panel.DebugRemoteCalls',
)

DEBUG_TOOLBAR_PANELS = DEFAULT_DEBUG_TOOLBAR_PANELS + LOCAL_DEBUG_TOOLBAR_PANELS

DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': '',  # rely on a version of jQuery that already exists
    'SHOW_TOOLBAR_CALLBACK': 'util.debug_toolbar.show_toolbar'   # override when the Django Debug Toolbar appears
}

# EDX-NOTIFICATIONS SUBSYSTEM

INSTALLED_APPS += (
    'edx_notifications.server.web',
)

# CLIENT BRANDING DEFAULT SETTINGS
LEARNER_DASHBOARD_BACKGROUND_IMAGE = "images/learner_dashboard/branding/backgrounds/"
LEARNER_DASHBOARD_LOGO_IMAGE = "images/learner_dashboard/branding/logos/"
LEARNER_DASHBOARD_RULE_COLOR = "#000000"
LEARNER_DASHBOARD_ICON_COLOR = "#000000"
DISCOVER_TITLE_COLOR = "#000000"
DISCOVER_AUTHOR_COLOR = "#000000"
DISCOVER_RULE_COLOR = "#000000"
LEARNER_DASHBOARD_BACKGROUND_COLOR = "#D3D3D3"
LEARNER_DASHBOARD_TOP_BAR_COLOR = "#ffffff"

#  LEARNER DASHBOARD DEFAULT SETTINGS
LEARNER_DASHBOARD_TITLE_COLOR = "#FFFFFF"
LEARNER_DASHBOARD_DESCRIPTION_COLOR = "#FFFFFF"

#  LEARNER DASHBOARD TILE DEFAULT SETTINGS
TILE_BACKGROUND_IMAGE = "images/learner_dashboard/tile_backgrounds/"
TILE_LABEL_COLOR = "#000000"
TILE_TITLE_COLOR = "#3384CA"
TILE_NOTE_COLOR = "#868685"
TILE_BACKGROUND_COLOR = "#FFFFFF"

# Characters added here will be cleaned in CSV exports data
CSV_CHARACTERS_BLACKLIST = [
    '+',
    '-',
    '=',
    '|',
    '!',
    '@',
    '#',
    '$',
    '%',
    '^',
    '&',
    '(',
    ')',
    ':',
    ';',
    '*'
]

# Controls how CSV formula injection characters are cleaned
# possible values are 'prepend', 'remove'
#
# prepend: Prepends apostrophe to value
# remove: Removes all the occurrences of blacklist characters
FORMULA_CLEAN_STRATEGY = 'prepend'

# Properties to clean
USER_PROPERTIES_TO_CLEAN = [
    'first_name',
    'last_name',
    'full_name',
    'title',
    'country',
    'city',
]

COMPANY_PROPERTIES_TO_CLEAN = [
    'full_name',
    'title',
    'address1',
    'address2',
    'city',
    'state',
    'country',
    'postal_code',
    'po',  # purchase order number
    'identity_provider',
]

CONTACT_PROPERTIES_TO_CLEAN = [
    'full_name',
    'title',
    'email',
    'phone',
]

COURSE_PROPERTIES_TO_CLEAN = [
    'name',
]

# Cache timeout settings
CACHE_TIMEOUTS = {
    'user_data': (60 * 1) * 30,  # 30 minutes
    'course_data': (60 * 1) * 30,
    'longterm_course_data': (60 * 60) * 24,  # 24 hours
    'group_data': (60 * 1) * 30,
    'org_data': (60 * 1) * 30,
    'common_data': (60 * 60) * 24,  # 24 hours
    'course_language': (60 * 60) * 24,
    'prefetched_course_data': (60 * 60) * 24,
}
DEFAULT_CACHE_TIMEOUT = (60 * 1) * 15  # 15 minutes

# default course depth to fetch from API
COURSE_DEFAULT_DEPTH = 3

# These URL prefixes are safe for Oauth2 communication
OAUTH2_SAFE_URL_PREFIXES = [
    'https://',
    'http://localhost:',
    'http://localhost/',
    'http://127.0.0.1:',
    'http://127.0.0.1/'
]

# Ooyala CDN url of Video Player V4
OOYALA_PLAYER_V4_SCRIPT_FILE = '//player.ooyala.com/core/10efd95b66124001b415aa2a4bee29c8?plugins=main,bm'

# storage directory fo stats/reports
EXPORT_STATS_DIR = 'csv_exports'

# Theme Settings

XBLOCK_THEME_CSS_PATH = 'mcka-theme/css/apros-xblocks.css'
XBLOCK_THEME_JS_PATH = 'mcka-theme/js/apros-xblocks.js'

# Course Key Regex
COURSE_KEY_PATTERN = r'(?P<course_key_string>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)'

# Foreign And Normal Characters Regex
FOREIGN_AND_NORMAL_CHARACTERS_PATTERN = \
    '[ŠŽšžŸÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖÙÚÛÜÝàáâãäåçèéêëìíîïðñòóôõöùúûüýÿ+ \w ]+'  # noqa: W605

# Cookies expiry time
COOKIES_YEARLY_EXPIRY_TIME = datetime.datetime.utcnow() + datetime.timedelta(days=365)

MAX_IMPORT_JOB_THREAD_POOL_SIZE = 4


# Rendering svg static files while running Django development server
import mimetypes  # noqa: E402

mimetypes.add_type("image/svg+xml", ".svg", True)
mimetypes.add_type("image/svg+xml", ".svgz", True)

# allowed mobile url schemes for SSO flow
MOBILE_URL_SCHEMES = [
    'mck',
    'mckinsey-mcka-debug',
    'mckinsey-rtsa-debug',
    'mckinsey-mcka-hla-debug',
    'mckinsey-horizon-debug',
    'mckinsey-mcka-stage',
    'mckinsey-rtsa-stage',
    'mckinsey-mcka-hla-stage',
    'mckinsey-horizon-stage',
    'mckinsey-mcka-release',
    'mckinsey-rtsa-release',
    'mckinsey-mcka-hla-release',
    'mckinsey-horizon-release',
]

REACT_NATIVE_UA_PREFIX = 'com.mcka.RNApp'
