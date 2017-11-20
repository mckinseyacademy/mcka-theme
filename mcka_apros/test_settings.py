# Test suite to be run with these settings
# contains test specific settings/overrides

from .settings import *

# for test environment, all http calls are safe
OAUTH2_SAFE_URL_PREFIXES = ['https://', 'http://', ]
