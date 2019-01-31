# Test suite to be run with these settings
# contains test specific settings/overrides

from .settings import *  # noqa: F403, F401, F405

# for test environment, all http calls are safe
OAUTH2_SAFE_URL_PREFIXES = ['https://', 'http://', ]

LOGGING = {}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mcka_apros',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

CELERY_ALWAYS_EAGER = True

GA_TRACKING_ID = 'test'
USE_I18N = True

ALLOWED_HOSTS = ['apros.mcka.local']

TEMPLATE_TEST_DIR = os.path.join(BASE_DIR, 'templates')  # noqa: F405
TEMPLATE_NEW_TEST_DIR = os.path.join(BASE_DIR, 'tests/templates_v2')  # noqa: F405

TEMPLATE_NEW_DIRS = [TEMPLATE_NEW_TEST_DIR]
