import os

from django.conf import settings

from django_assets import Bundle, register

os.environ['SASS_USE_SCSS'] = 'false'


def get_assets_v2_path(relative_path):
    V2_ROOT = str(os.path.join(settings.BASE_DIR, settings.ASSETS_ROOT_V2))
    return str(os.path.join(V2_ROOT, relative_path))


# Javascript squashing
JS = Bundle(
    get_assets_v2_path('js/vendor/jquery.form.js'),
    get_assets_v2_path('js/custom.js'),
    get_assets_v2_path('js/common.js'),
    get_assets_v2_path('js/application.js'),
    filters='jsmin',
    output='gen/packed_v2.js'
)
register('js_all_v2', JS)

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

SCSS_LTR_V2 = Bundle(
    get_assets_v2_path('scss/ltr.scss'),
    filters='libsass',
    output='gen/ltr_v2.css',
    depends=('scss/**/*.scss')
)
register('scss_ltr_v2', SCSS_LTR_V2)

CSS_LTR_V2 = Bundle(
    SCSS_LTR_V2,
    filters='cssmin',
    output='gen/packed_ltr_v2.css'
)
register('css_ltr_v2', CSS_LTR_V2)

SCSS_RTL_V2 = Bundle(
    get_assets_v2_path('scss/rtl.scss'),
    filters='libsass',
    output='gen/rtl_v2.css',
    depends=('scss/**/*.scss')
)
register('scss_rtl_v2', SCSS_RTL_V2)

CSS_RTL_V2 = Bundle(
    SCSS_RTL_V2,
    filters='cssmin',
    output='gen/packed_rtl_v2.css'
)
register('css_rtl_v2', CSS_RTL_V2)
