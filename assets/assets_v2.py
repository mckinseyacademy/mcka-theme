import os

from django.conf import settings

from django_assets import Bundle, register

os.environ['SASS_USE_SCSS'] = 'false'


def get_assets_v2_path(relative_path):
    V2_ROOT = str(os.path.join(settings.BASE_DIR, settings.ASSETS_ROOT_V2))
    return str(os.path.join(V2_ROOT, relative_path))


# CSS compilation and squashing
# Core CSS

SCSS_CORE_V2 = Bundle(
    get_assets_v2_path('scss/core.scss'),
    filters='libsass',
    output='gen/core_v2.css',
)
register('scss_core_v2', SCSS_CORE_V2)

CSS_CORE_V2 = Bundle(
    SCSS_CORE_V2,
    filters='cssmin',
    output='gen/packed_core_v2.css'
)
register('css_core_v2', CSS_CORE_V2)
