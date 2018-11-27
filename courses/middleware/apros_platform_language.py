import re

from django.conf import settings

from util.i18n_helpers import set_language
from api_data_manager.course_data import CourseDataManager


class AprosPlatformLanguage(object):
    """Middleware for switching platform language according to visiting pages, Course related
    pages to be translated in course language, Admin site should be translated to English and
    general pages including login,home,faq, terms, activation and privacy should be in browser's
    preferred language."""

    def _get_browser_preferred_language(self, request):
        if request.META.get('HTTP_ACCEPT_LANGUAGE'):
            language = request.META.get('HTTP_ACCEPT_LANGUAGE').split(',')[0]
            language_without_variant = language.split('-')[0]
            return language_without_variant

    def process_request(self, request):
        if settings.USE_I18N:
            self._enable_internationalization(request)
        else:
            set_language(settings.LANGUAGE_CODE)

    def _enable_internationalization(self, request):
        path = request.path
        language = None
        if path.startswith('/jsi18n/'):
            return None
        if path.startswith('/courses') and request.user.is_authenticated:
            try:
                course_id = re.search(settings.COURSE_KEY_PATTERN, path[8:]).group(0)
                language = CourseDataManager(course_id).get_language(request.user.id)
            except Exception:
                return None

        elif path.startswith('/admin'):
            language = 'en-us'
        elif not request.user.is_authenticated:
            language = request.COOKIES.get(
                'preferred_language',
                self._get_browser_preferred_language(request))
        else:
            return None
        set_language(language)
