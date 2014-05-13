from django_assets import Bundle, register
import os

os.environ['SASS_USE_SCSS'] = 'false'

# Javascript squashing
JS = Bundle(
    'js/polyfills/*.js',
    'js/vendor/leaflet.js',
    'js/vendor/json2.js',
    'js/vendor/underscore.js',
    'js/vendor/backbone.js',
    'js/vendor/d3.v3.js',
    'js/vendor/nv.d3.js',
    'js/application.js',
    'js/router.js',
    'js/models/**/*.js',
    'js/views/**/*.js',
    filters='jsmin',
    output='packed.js'
)
register('js_all', JS)

# CSS compilation and squashing
SCSS = Bundle(
    'scss/app.scss',
    filters='sass',
    output='app.css',
    depends=('scss/**/*.scss')
)
register('scss_all', SCSS)

CSS = Bundle(
    SCSS,
    output='packed.css'
)
register('css_all', CSS)
