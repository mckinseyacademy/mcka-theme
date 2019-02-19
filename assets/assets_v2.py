import os
from django_assets import Bundle, register

from .utils import _build_file_list, get_assets_path

os.environ['SASS_USE_SCSS'] = 'false'


js_files = []

js_files.extend(_build_file_list("js/plugins", ".js"))

js_files.extend([
    get_assets_path('js/vendor/jquery.form.js', v2=False),
    get_assets_path('js/vendor/jquery.touchwipe.min.js', v2=False),
    get_assets_path('js/vendor/backbone.js', v2=False),
    get_assets_path('js/vendor/backbone.paginator.js', v2=False),
    get_assets_path('js/vendor/jquery.clearsearch.js', v2=False),
    get_assets_path('js/vendor/bbGrid.js', v2=False),

    get_assets_path('js/custom.js', v2=True),
    get_assets_path('js/common.js', v2=True),
    get_assets_path('js/application.js', v2=True),
    get_assets_path('js/jquery.mCustomScrollbar.concat.min.js', v2=True),

    get_assets_path('js/router.js', v2=False),
    get_assets_path('js/config.js', v2=False),
    get_assets_path('js/utils.js', v2=False),
])

js_files.extend(_build_file_list("js/common", ".js", v2=False))
js_files.extend(_build_file_list("js/models", ".js", v2=False))
js_files.extend(_build_file_list("js/collections", ".js", v2=False))
js_files.extend(_build_file_list("js/views", ".js", v2=False))

# Javascript squashing
JS = Bundle(
    *js_files,
    filters='jsmin',
    output='gen/packed_v2.js'
)

register('js_all_v2', JS)

# CSS compilation and squashing
# Core CSS

SCSS_CORE_V2 = Bundle(
    get_assets_path('scss/core.scss', v2=True),
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
    get_assets_path('scss/ltr.scss', v2=True),
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
    get_assets_path('scss/rtl.scss', v2=True),
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
