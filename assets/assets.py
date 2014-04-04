from django_assets import Bundle, register
import os

os.environ['SASS_USE_SCSS'] = 'false'

# Javascript squashing
JS = Bundle(
    'js/vendor/jquery.js',
    'js/application.js',
    filters='jsmin',
    output='packed.js'
)
register('js_all', JS)

# CSS compilation and squashing
SCSS = Bundle(
    'scss/app.scss',
    filters='sass',
    output='app.css',
    depends=('scss/*.scss')
)
register('scss_all', SCSS)

CSS = Bundle(
    SCSS,
    filters='cssmin',
    output='packed.css'
)
register('css_all', CSS)
