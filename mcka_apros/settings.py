"""
Django settings for academy project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from logsettings import get_logger_config
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1x@epyq-))w6z8a@_9f+c8%g#n8o75jeh8c8d4_&y+f@2_(des'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ASSETS_SOURCE_ROOT = 'static'

LOGGING = get_logger_config(BASE_DIR,
                            logging_env="dev",
                            tracking_filename="tracking.log",
                            dev_env=True,
                            debug=True)

TEMPLATE_DEBUG = True

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
    'south',
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
    'rest_framework',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

SOUTH_MIGRATION_MODULES = {
    'accounts': 'accounts.migrations',
    'admin': 'admin.migrations',
    'main': 'main.migrations',
    'license': 'license.migrations',
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.session_timeout.SessionTimeout',
    'accounts.middleware.thread_local.ThreadLocal',
    'debug_toolbar.middleware.DebugToolbarMiddleware',      # explicitly add this, otherwise this doesn't seem to appear on AWS environments
    'accounts.middleware.ajax_redirect.AjaxRedirect',
    'lib.middleware.handle_prior_ids.PriorIdRequest',
)

ROOT_URLCONF = 'mcka_apros.urls'

WSGI_APPLICATION = 'mcka_apros.wsgi.application'

AUTHENTICATION_BACKENDS = (
    #'django.contrib.auth.backends.ModelBackend',
    'accounts.json_backend.JsonBackend',
)

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

TEMPLATE_LOADERS = (
    'hamlpy.template.loaders.HamlPyFilesystemLoader',
    'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_cache')
MEDIA_ROOT = ''
ASSETS_ROOT = 'static/gen'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "static/gen"),
)

#Handle session is not Json Serializable
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# We want a different name for cookies than on the LMS to allow to set
# the LMS cookies at the domain level from apros
SESSION_COOKIE_NAME = 'apros_sessionid'
CSRF_COOKIE_NAME = 'apros_csrftoken'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_TIMEOUT_SECONDS = 300

# LMS
LMS_BASE_DOMAIN = 'mckinseyacademy.com'
LMS_SUB_DOMAIN = 'lms'
LMS_PORT = None
LMS_SESSION_COOKIE_DOMAIN = None  # Default: use current/same domain
# LMS_AUTH_URL: relative or absolute URL to the LMS's /auth/ urls, used for SSO.
# Normally this is on the same domain as Apros and is forwarded to the LMS by an nginx reverse proxy rule
LMS_AUTH_URL = '/auth/'

NO_PROGRAM_NAME = "McKinsey Management Program"
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
API_MOCK_SERVER_ADDRESS = 'http://openedxapi.apiary-mock.com'

RUN_LOCAL_MOCK_API = False
LOCAL_MOCK_API_FILES = [
    os.path.join(BASE_DIR, 'apiary.apib'),
    os.path.join(BASE_DIR, 'mock_supplementals.apib'),
]

# EdX Api Key
# Set this on OpenEdx server, and within production environment to whichever value is desired
EDX_API_KEY = 'test_api_key'

# edX LMS shared secret used to validate provider data during SSO logins
EDX_SSO_DATA_HMAC_KEY = '1private_apros_key'

# A list of the provider_id values of any SSO providers for which we want the SSO user
# registration process to be as fast as possible, skipping the registration form completely.
# Provider IDs for the default SAML provider are of the form "saml-[slug]" where [slug] is the
# "IdP Slug" value in /admin/third_party_auth/samlproviderconfig/
SSO_AUTOPROVISION_PROVIDERS = ["saml-mckinsey"]

# When autoprovisioning (see previous setting), set the user's city to this value. (A city is
# required for things like the map of students, but we don't get 'city' from the SSO provider.)
SSO_AUTOPROVISION_CITY = "Gotham"

# Whether or not to cache courseware content locally, defult=False but can be overridden in local_settings.py
USE_SESSION_COURSEWARE_CACHING = False

# Goog Analytics Tracking ID
GA_TRACKING_ID = None # should be UA-48573128-1 for McKA production

# While we have TA email group, define it here
TA_EMAIL_GROUP = 'tas@mckinseyacademy.com'
INITIAL_PASSWORD = 'PassworD12!@'

# Email address students get their enrollment email sent from
ENROLL_STUDENT_EMAIL = 'support@mckinseyacademy.com'

# Disabling automatic program enrollment for no (MCKIN-1750)
ENABLE_AUTOMATIC_EMAILS_UPON_PROGRAM_ENROLLMENT = False

# EMAIL BACKEND
EMAIL_BACKEND = "django_ses.SESBackend"
APROS_EMAIL_SENDER = "no-reply@mckinseyacademy.com"

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

# Api locations
COURSEWARE_API = '/'.join([API_SERVER_PREFIX, 'courses'])
GROUP_API = '/'.join([API_SERVER_PREFIX, 'groups'])
ORGANIZATION_API = '/'.join([API_SERVER_PREFIX, 'organizations'])
PROJECT_API = '/'.join([API_SERVER_PREFIX, 'projects'])
AUTH_API = '/'.join([API_SERVER_PREFIX, 'sessions'])
USER_API = '/'.join([API_SERVER_PREFIX, 'users'])
WORKGROUP_API = '/'.join([API_SERVER_PREFIX, 'workgroups'])

# set AWS querystring authentication to false
AWS_QUERYSTRING_AUTH = False

# Components whose contents do not count towards progress calculation
PROGRESS_IGNORE_COMPONENTS = [
    'discussion-course',
    'group-project',
    'discussion-forum',

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
    "normal": "#b1c2cc",# $mckinsey-academy-blue-gray
    "dropped": "#e5ebee",# $mckinsey-academy-bright-gray
    "group_work": "#66a5b5",# $mckinsey-academy-turquoise
    "total": "#e37222",# $mckinsey-orange
    "proforma": "none",
}

# Mapbox settings
MAPBOX_API = {
    'map_id': 'mckinseyacademy.i2hg775e',
    'public_token': 'pk.eyJ1IjoibWNraW5zZXlhY2FkZW15IiwiYSI6ImpXeXZfM0UifQ.U9z171wwWYtDbn_Fv-6nlg',
    'secret_token': 'sk.eyJ1IjoibWNraW5zZXlhY2FkZW15IiwiYSI6Im9vX1JtRmcifQ.cW8tajahj-HfnK00IsD9qg',
}

# image sizes to generate from the originally uploaded file
PROFILE_GENERATE_IMAGE_SIZES = [[48, 48], [160, 160]]
COMPANY_GENERATE_IMAGE_SIZES = [[140, 40], [175, 50]]
# remove any of these sizes while regenerating the changed images
PROFILE_REMOVE_IMAGE_SIZES = [40, 120]
COMPANY_REMOVE_IMAGE_SIZES = [40, 120, 80, 160]

TEMP_IMAGE_FOLDER = "profile_temp_images/"

FEATURES = {
    'notes': False,
}

try:
    from local_settings import *
except ImportError:
    pass

# Include any apps added from switch set in local_settings
if RUN_LOCAL_MOCK_API:
    INSTALLED_APPS += (
        'mockapi',
    )

# Add request object to templates
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    'lib.context_processors.user_program_data',
    'lib.context_processors.settings_data',
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

DAILY_EMAIL_REPORTS_CONFIG = {
    #email stuff
    "smtp_server":"smtp.gmail.com",
    "smtp_port":"587",
    "smtp_user_email":"systembot@mckinseyacademy.com", #TODO:add user email
    "smtp_user_password":"YesniKcM123", #TODO: add user password
    "email_to":"vishal@mckinseyacademy.com", #TODO: add daily stats email
    "email_from":"vishal@mckinseyacademy.com", #TODO: add from email
    "date_format":"%d/%m/%Y",
    "email_space":", ",
    "data":"related",
    #build script stuff
    "output_directory":"analytics/output/",
    "edx_db_name":"edx",
    "apros_db_name":"default",
    "file_format":".xlsx",
}

################################### EDX-NOTIFICATIONS SUBSYSTEM ######################################

INSTALLED_APPS += (
    'edx_notifications.server.web',
)

TEMPLATE_LOADERS += (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

LEARNER_DASHBOARD_ENABLED = True

#File upload paths for Learner Dashboard
LOGO = "static/image/learner_dashboard/branding/logos/"
BACKGROUND = "static/image/learner_dashboard/branding/backgrounds/"
TILE_BACKGROUND = "static/image/learner_dashboard/tile_backgrounds/"
RESOURCES = "static/image/learner_dashboard/resources/"
# Default settings for Learner Dashboard Client Branding
BACKGROUND_IMAGE = None
LOGO_IMAGE = None
NAVIGATION_COLORS = None
TEXT_COLORS = None
BACKGROUND_TILED = None
