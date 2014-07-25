from django_assets import Bundle, register
import os

os.environ['SASS_USE_SCSS'] = 'false'

# Javascript squashing
JS = Bundle(
    'js/polyfills/*.js',
    'js/plugins/*.js',
    'js/vendor/jquery.form.js',
    'js/vendor/leaflet.js',
    'js/vendor/json2.js',
    'js/vendor/underscore.js',
    'js/vendor/backbone.js',
    'js/vendor/d3.v3.js',
    'js/vendor/nv.d3.js',
    'js/vendor/dataTables.foundation.js',
    'js/application.js',
    'js/router.js',
    'js/models/**/*.js',
    'js/views/**/*.js',
    filters='jsmin',
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
    output='packed_admin.css'
)
register('css_admin', CSS_ADMIN)
