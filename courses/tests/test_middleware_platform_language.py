from django.test import TestCase, RequestFactory
import ddt
from django.utils import translation

from accounts.tests.utils import ApplyPatchMixin
from courses.middleware.apros_platform_language import AprosPlatformLanguage
from lib.utils import DottableDict
from mcka_apros.settings import LANGUAGE_CODE


@ddt.ddt
class TestAprosPlatformLanguage(TestCase, ApplyPatchMixin):
	''' Test middleware apros_platform_language of courses '''

	def setUp(self):
		self.apros_platform_language = AprosPlatformLanguage()
		self.factory = RequestFactory()

	def mock_request_object(self, path, language_code):
		'''
		Mocking the actual request to use in test cases
		:param path: relative path for url to be build for request
		:param language_code: language code for browser's
		'''
		request = self.factory.get(path)
		request.META['HTTP_ACCEPT_LANGUAGE'] = language_code
		request.LANGUAGE_CODE = 'jp'
		request.session = {}
		request.user = DottableDict({'id': 1, 'is_authenticated': lambda: True})
		return request

	@ddt.data(
		('jp,de-DE,de;q=0.8,en-GB;q=0.6,en;q=0.4', 'jp'),
		('ar,de-DE', 'ar'),
		('en', 'en')
	)
	@ddt.unpack
	def test_get_browser_preferred_language(self, codes, expected_language):
		"""
		:param codes: Browser's language
		:param expected_language: expected language of browser after cleaning the string
		"""
		request = self.mock_request_object('/', codes)
		language = self.apros_platform_language._get_browser_preferred_language(request)
		self.assertEquals(expected_language, language)

	@ddt.data(
		('/courses/arbisoft/1/1', 'ar'),
		('/courses/mckinsey/3/3/lessons/i4x://mckinsey/3/', 'ar'),
		('/courses/arbisSOFT/SAMPLe/1', 'ar'),
		('/courses/arbisoft/TEst123/TEST', 'ar'),
		('/courses/arbisoft/Test12abc/1/', 'ar'),
		('/', 'en'),
		('/accounts/login/', 'en'),
		('/faq/', 'en'),
		('/privacy/', 'en'),
		('/terms/', 'en'),
		('/accounts/activate/123basdyadq', 'en'),
		('/admin/', LANGUAGE_CODE),
		('/admin/clients/1/navigation', LANGUAGE_CODE)
	)
	@ddt.unpack
	def test_process_request(self, path, expected_language):
		"""
		:param path: Relative url for parsing
		:param expected_language: language of platform which is expected
		"""
		request = self.mock_request_object(path, 'en,jp,de-DE,en-GB;q=0.6')

		get_current_request = self.apply_patch('util.i18n_helpers.get_current_request')
		get_current_request.return_value = request

		course_detail = self.apply_patch('courses.middleware.apros_platform_language.user_api')
		course_detail.get_user_course_detail.return_value = DottableDict({'language': 'ar'})

		self.apros_platform_language.process_request(request)
		self.assertEqual(expected_language, translation.get_language())
		self.assertEqual(expected_language, request.session[translation.LANGUAGE_SESSION_KEY])

	def test_process_request_with_invalid_course_url(self):
		"""
		:param path: Url for invalid course_id
		"""
		request = self.mock_request_object('/courses/', 'jp,de-DE,en-GB;q=0.6,en')
		self.assertIsNone(self.apros_platform_language.process_request(request))
