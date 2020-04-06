import os
from django_assets import Bundle, register

from .utils import build_file_list, get_assets_path

os.environ['SASS_USE_SCSS'] = 'false'


js_files = []

js_files.extend(build_file_list("js/plugins", ".js"))

js_files.extend([
    get_assets_path('js/vendor/jquery.form.js', v2=False),
    get_assets_path('js/vendor/jquery.touchwipe.min.js', v2=False),
    get_assets_path('js/vendor/jquery.md5.js', v2=False),
    get_assets_path('js/vendor/backbone.js', v2=False),
    get_assets_path('js/vendor/backbone.paginator.js', v2=False),
    get_assets_path('js/vendor/jquery.clearsearch.js', v2=False),
    get_assets_path('js/vendor/bbGrid.js', v2=False),
    get_assets_path('js/vendor/moment-with-locales.min.js', v2=False),
    get_assets_path('js/vendor/moment-timezone.js', v2=False),
    get_assets_path('js/vendor/moment-timezone-with-data.js', v2=False),
    get_assets_path('js/vendor/date.js', v2=False),
    get_assets_path('js/highcharts/highcharts.js', v2=False),
    get_assets_path('js/highcharts/highcharts-more.js', v2=False),

    get_assets_path('js/custom.js', v2=True),
    get_assets_path('js/common.js', v2=True),
    get_assets_path('js/application.js', v2=True),
    get_assets_path('js/jquery.mCustomScrollbar.concat.min.js', v2=True),
    get_assets_path('js/course_learner_dashboard/utils.js', v2=True),

    get_assets_path('js/router.js', v2=False),
    get_assets_path('js/config.js', v2=False),
    get_assets_path('js/utils.js', v2=False),

    get_assets_path('js/css-vars-ponyfill.js', v2=True),
    get_assets_path('js/vendor/jquery.cookie.js', v2=False),
    get_assets_path('js/vendor/jquery.xblock.js', v2=False),
    get_assets_path('js/bootstrap.bundle.min.js', v2=True),
    get_assets_path('js/session_timeout_timer.js', v2=False),
    get_assets_path('js/image_editor.js', v2=True),
    get_assets_path('js/vendor/cropper.min.js', v2=False),
    get_assets_path('js/user_profile_edit_v2.js', v2=True),

    get_assets_path('js/ajaxify_overlay_form.js', v2=True),
    get_assets_path('js/vendor/jquery.query-object.js', v2=True),
    get_assets_path('js/vendor/js.cookie.js', v2=True),
    get_assets_path('js/accounts/user_login.js', v2=True),

    get_assets_path('js/course_contact_modal.js', v2=False),
    get_assets_path('js/course_learner_dashboard/tile_id_to_view.js', v2=False),
    get_assets_path('js/course_learner_dashboard/learner_dashboard_calendar_load.js', v2=True),
    get_assets_path('js/jquery.mCustomScrollbar.concat.min.js', v2=True),
    get_assets_path('js/app_link_popup.js', v2=False),

    get_assets_path('js/course_learner_dashboard/tile_progress_update.js', v2=True),
    get_assets_path('js/course_lesson.js', v2=False),

    get_assets_path('js/course_learner_dashboard/lesson_url_to_view.js', v2=True),
    get_assets_path('js/course_contact.js', v2=True),
])

js_files.extend(build_file_list("js/common", ".js", v2=False))
js_files.extend(build_file_list("js/models", ".js", v2=False))
js_files.extend(build_file_list("js/collections", ".js", v2=False))
js_files.extend(build_file_list("js/views", ".js", v2=False))

# site-wide JS
JS = Bundle(
    *js_files,
    filters='jsmin',
    output='gen/packed_v2.js'
)

register('js_all_v2', JS)

# site-wide CSS
SCSS_CORE_V2 = Bundle(
    get_assets_path('scss/core.scss', v2=True),
    filters='libsass',
    output='gen/core_v2.css',
)
core_css_files = [
    SCSS_CORE_V2,
    get_assets_path('css/cropper.css', v2=False),
]

CSS_CORE_V2 = Bundle(
    *core_css_files,
    filters='cssmin',
    output='gen/packed_core_v2.css'
)
register('css_core_v2', CSS_CORE_V2)

CSS_LTR_V2 = Bundle(
    get_assets_path('scss/ltr.scss', v2=True),
    filters='libsass',
    output='gen/ltr_v2.css',
    depends='scss/**/*.scss'
)

register('css_ltr_v2', CSS_LTR_V2)

CSS_RTL_V2 = Bundle(
    get_assets_path('scss/rtl.scss', v2=True),
    filters='libsass',
    output='gen/rtl_v2.css',
    depends='scss/**/*.scss'
)

register('css_rtl_v2', CSS_RTL_V2)
