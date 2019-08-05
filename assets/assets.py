import os
from django_assets import Bundle, register

from .utils import _build_file_list

os.environ['SASS_USE_SCSS'] = 'false'

js_ie8_files = []
js_ie8_files.extend(_build_file_list("js/polyfills", ".js"))
js_ie8_files.extend(_build_file_list("js/plugins", ".js"))
js_ie8_files.extend([
    'js/vendor/jquery.form.js',
    'js/vendor/json2.js',
    'js/vendor/underscore.js',
    'js/vendor/backbone.js',
    'js/vendor/Backbone.CrossDomain.js',
    'js/vendor/backbone.paginator.js',
    # 'js/vendor/d3.v3.js',
    # 'js/vendor/nv.d3.js',
    'js/vendor/dataTables.foundation.js',
    'js/vendor/jquery.dataTables.rowGrouping.js',
    'js/vendor/bbGrid.js',
    'js/vendor/jquery-ui.min.js',
    'js/vendor/jquery.clearsearch.js',
    'js/vendor/countrySelect.min.js',
    'js/vendor/dropzone.js',
    'js/application.js',
    'js/router.js',
])
js_ie8_files.extend(_build_file_list("js/common", ".js"))
js_ie8_files.extend(_build_file_list("js/models", ".js"))
js_ie8_files.extend(_build_file_list("js/collections", ".js"))
js_ie8_files.extend(_build_file_list("js/views", ".js"))
# Javascript squashing
JS_IE8 = Bundle(
    *js_ie8_files,
    filters='jsmin',
    output='gen/packed_ie8.js'
)
register('js_ie8', JS_IE8)

js_files = []
js_files.extend(_build_file_list("js/polyfills", ".js"))
js_files.extend(_build_file_list("js/plugins", ".js"))
js_files.extend([
    'js/vendor/jquery.form.js',
    'js/vendor/json2.js',
    'js/vendor/underscore.js',
    'js/vendor/backbone.js',
    'js/vendor/Backbone.CrossDomain.js',
    'js/vendor/backbone.paginator.js',
    'js/vendor/d3.v3.js',
    'js/vendor/nv.d3.js',
    'js/vendor/dataTables.foundation.js',
    'js/vendor/jquery.dataTables.rowGrouping.js',
    'js/vendor/jquery.touchwipe.min.js',
    'js/vendor/moment-with-locales.min.js',
    'js/vendor/moment-timezone.js',
    'js/vendor/moment-timezone-with-data.js',
    'js/vendor/bbGrid.js',
    'js/vendor/jquery-ui.min.js',
    'js/vendor/jquery.clearsearch.js',
    'js/vendor/countrySelect.min.js',
    'js/vendor/dropzone.js',
    'js/application.js',
    'js/router.js',
    'js/config.js',
    'js/utils.js',
])
js_files.extend(_build_file_list("js/common", ".js"))
js_files.extend(_build_file_list("js/models", ".js"))
js_files.extend(_build_file_list("js/collections", ".js"))
js_files.extend(_build_file_list("js/views", ".js"))

# Javascript squashing
JS = Bundle(
    *js_files,
    # filters='jsmin',
    output='gen/packed.js'
)
register('js_all', JS)

# CSS compilation and squashing
# Core CSS

SCSS_CORE = Bundle(
    'scss/core.scss',
    filters='libsass',
    output='gen/core.css',
    depends=('scss/**/*.scss')
)
register('scss_core', SCSS_CORE)

CSS_CORE = Bundle(
    SCSS_CORE,
    filters='cssmin',
    output='gen/packed_core.css'
)
register('css_core', CSS_CORE)

# Applicaiton CSS
SCSS_APP = Bundle(
    'scss/app.scss',
    filters='libsass',
    output='gen/app.css',
    depends=('scss/**/*.scss')
)
register('scss_app', SCSS_APP)

CSS_APP = Bundle(
    SCSS_APP,
    filters='cssmin',
    output='gen/packed_app.css'
)
register('css_app', CSS_APP)

# Admin CSS
SCSS_ADMIN = Bundle(
    'scss/admin.scss',
    filters='libsass',
    output='gen/admin.css',
    depends=('scss/**/*.scss')
)
register('scss_admin', SCSS_ADMIN)

CSS_ADMIN = Bundle(
    SCSS_ADMIN,
    filters='cssmin',
    output='gen/packed_admin.css'
)
register('css_admin', CSS_ADMIN)

# IE8 Overries
SCSS_IE8 = Bundle(
    'scss/ie8.scss',
    filters='libsass',
    output='gen/ie8.css',
    depends=('scss/**/*.scss')
)
register('scss_ie8', SCSS_IE8)

CSS_IE8 = Bundle(
    SCSS_IE8,
    filters='cssmin',
    output='gen/packed_ie8.css'
)
register('css_ie8', CSS_IE8)

# Internationalization CSS
SCSS_RTL = Bundle(
    'scss/rtl.scss',
    filters='libsass',
    output='gen/rtl.css',
    depends=('scss/**/*.scss')
)
register('scss_rtl', SCSS_RTL)

CSS_RTL = Bundle(
    SCSS_RTL,
    filters='cssmin',
    output='gen/packed_rtl.css'
)
register('css_rtl', CSS_CORE)

SCSS_LTR = Bundle(
    'scss/ltr.scss',
    filters='libsass',
    output='gen/ltr.css',
    depends=('scss/**/*.scss')
)
register('scss_ltr', SCSS_LTR)

CSS_LTR = Bundle(
    SCSS_LTR,
    filters='cssmin',
    output='gen/packed_ltr.css'
)
register('css_ltr', CSS_LTR)
