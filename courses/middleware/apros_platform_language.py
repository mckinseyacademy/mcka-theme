import re

from django.http import Http404

from api_client import user_api
from api_client.api_error import ApiError
from mcka_apros.settings import LANGUAGE_CODE, COURSE_KEY_PATTERN
from util.i18n_helpers import set_language


class AprosPlatformLanguage(object):
	"""Middleware for switching platform language according to visiting pages, Course related
	pages to be translated in course language, Admin site should be translated to English and
	general pages including login,home,faq, terms, activation and privacy should be in browser's
	preferred language."""

	def _get_browser_preferred_language(self, request):
		if request.META.get('HTTP_ACCEPT_LANGUAGE'):
			return request.META.get('HTTP_ACCEPT_LANGUAGE').split(',')[0]

	def process_request(self, request):
		path = request.path
		language = None
		general_pages = [
			'/accounts/login/',
			'/faq/',
			'/privacy/',
			'/terms/',
			'/',
		]
		if path.startswith('/courses') and request.user.is_authenticated():
			try:
				course_id = re.search(COURSE_KEY_PATTERN, path[8:]).group(0)
				course_detail = user_api.get_user_course_detail(request.user.id, course_id)
			except Exception:
				return None
			if course_detail.language:
				language = course_detail.language
		elif path in general_pages or path.startswith('/accounts/activate/'):
			language = request.COOKIES.get(
				'preferred_language',
				self._get_browser_preferred_language(request))
		set_language(language)