# Test suite to be run with these settings
# contains test specific settings/overrides

from .settings import *  # noqa: F403, F401

# for test environment, all http calls are safe
OAUTH2_SAFE_URL_PREFIXES = ['https://', 'http://', ]

CELERY_ALWAYS_EAGER = True

GA_TRACKING_ID = 'test'
USE_I18N = True

ALLOWED_HOSTS = ['apros.mcka.local']
