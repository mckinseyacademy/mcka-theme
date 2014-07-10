"""
Django settings for academy project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1x@epyq-))w6z8a@_9f+c8%g#n8o75jeh8c8d4_&y+f@2_(des'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

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
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.session_timeout.SessionTimeout',
    'accounts.middleware.thread_local.ThreadLocal',
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
SESSION_TIMEOUT_SECONDS = 300

# LMS
LMS_BASE_DOMAIN = 'mckinseyacademy.com'
LMS_SUB_DOMAIN = 'lms'

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

# Target number of reviews for a group project
GROUP_REVIEWS_TARGET = 3

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
