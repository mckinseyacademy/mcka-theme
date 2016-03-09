import os

from django.conf import settings

from django_assets import Bundle, register

os.environ['SASS_USE_SCSS'] = 'false'

def _build_file_list(folder, ext):
    current_dir = os.getcwd()
    os.chdir(os.path.join(settings.ASSETS_SOURCE_ROOT, folder))
    matching_files = []
    for root, dirs, files in os.walk('.',topdown=True):
        folder_root = root.split('/')
        folder_root[0] = folder
        folder_name = '/'.join(folder_root)

        matching_files.extend(["/".join([folder_name,name]) for name in files if os.path.splitext(name)[-1]==ext])

    os.chdir(current_dir)

    return matching_files

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
    #'js/vendor/d3.v3.js',
    #'js/vendor/nv.d3.js',
    'js/vendor/dataTables.foundation.js',
    'js/vendor/jquery.dataTables.rowGrouping.js',
    'js/vendor/bbGrid.js',
    'js/vendor/jquery-ui.min.js', 
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
    output='packed_ie8.js'
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
    'js/vendor/bbGrid.js',
    'js/vendor/jquery-ui.min.js',
    'js/application.js',
    'js/router.js',
])
js_files.extend(_build_file_list("js/common", ".js"))
js_files.extend(_build_file_list("js/models", ".js"))
js_files.extend(_build_file_list("js/collections", ".js"))
js_files.extend(_build_file_list("js/views", ".js"))

# Javascript squashing
JS = Bundle(
    *js_files,
    # filters='jsmin',
    output='packed.js'
)
register('js_all', JS)

# CSS compilation and squashing
# Core CSS
SCSS_CORE = Bundle(
    'scss/core.scss',
    filters='sass',
    output='core.css',
    depends=('scss/**/*.scss')
)
register('scss_core', SCSS_CORE)

CSS_CORE = Bundle(
    SCSS_CORE,
    filters='cssmin',
    output='packed_core.css'
)
register('css_core', CSS_CORE)

# Applicaiton CSS
SCSS_APP = Bundle(
    'scss/app.scss',
    filters='sass',
    output='app.css',
    depends=('scss/**/*.scss')
)
register('scss_app', SCSS_APP)

CSS_APP = Bundle(
    SCSS_APP,
    filters='cssmin',
    output='packed_app.css'
)
register('css_app', CSS_APP)

# Admin CSS
SCSS_ADMIN = Bundle(
    'scss/admin.scss',
    filters='sass',
    output='admin.css',
    depends=('scss/**/*.scss')
)
register('scss_admin', SCSS_ADMIN)

CSS_ADMIN = Bundle(
    SCSS_ADMIN,
    filters='cssmin',
    output='packed_admin.css'
)
register('css_admin', CSS_ADMIN)

# IE8 Overries
SCSS_IE8 = Bundle(
    'scss/ie8.scss',
    filters='sass',
    output='ie8.css',
    depends=('scss/**/*.scss')
)
register('scss_ie8', SCSS_IE8)

CSS_IE8 = Bundle(
    SCSS_IE8,
    filters='cssmin',
    output='packed_ie8.css'
)
register('css_ie8', CSS_IE8)
