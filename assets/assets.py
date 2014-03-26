from django_assets import Bundle, register
import os

os.environ['SASS_USE_SCSS'] = 'false'

# Javascript squashing
js = Bundle(
	'js/vendor/jquery.js',
	'js/application.js',
   	filters='jsmin', 
   	output='packed.js'
)
register('js_all', js)

# CSS compilation and squashing
scss = Bundle(
	'scss/app.scss',
	filters='sass', 
	output='app.css',
	depends=('scss/*.scss')
)
register('scss_all', scss)

css = Bundle(
	scss,
   	filters='cssmin', 
   	output='packed.css'
)
register('css_all', css)
