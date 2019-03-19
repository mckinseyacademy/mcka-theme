import traceback
import mock

from django.test import TestCase, override_settings

from courses.user_courses import CURRENT_PROGRAM
from courses.views import infer_page_navigation
from api_data_manager.tests.utils import mock_api_data_manager


class InferPageNavigationTests(TestCase):
    def _make_patch(self, target, new_value=None):
        new_val = new_value \
            if new_value else mock.Mock()
        patcher = mock.patch(target, new_val)
        patched = patcher.start()

        self.addCleanup(patcher.stop)
        return patched

    # noinspection PyMethodMayBeStatic
    def _get_request_mock(self, user_id, course_id):
        request_mock = mock.Mock()
        request_mock.user.id = user_id

        course_mock = mock.Mock()
        course_mock.id = course_id
        course_mock.started = True
        request_mock.course = course_mock
        program_mock = mock.Mock()
        program_mock.courses = [course_mock]

        # needed to pass check_user_course_access decorator
        request_mock.session = {CURRENT_PROGRAM: program_mock}
        return request_mock

    def setUp(self):

        self.load_course_mock = self._make_patch('courses.views.load_course')
        self.user_api_mock = self._make_patch('courses.views.user_api')
        self.get_group_project_for_user_course_mock = \
            self._make_patch('courses.views.get_group_project_for_user_course')
        self.get_group_project_for_user_course_mock.return_value = (None, None)

        self.get_chapter_and_target_by_location_mock = \
            self._make_patch('courses.views.get_chapter_and_target_by_location')
        self.get_chapter_and_target_by_location_mock.return_value = ('chapter_id', 'vertical_id', 'final_target_id')

    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
    def test_infer_page_navigation_no_group_work_does_not_crash(self):
        request = self._get_request_mock(1, 'course_id')
        mock_api_data_manager(
            module_path='accounts.middleware.thread_local.UserDataManager',
            data={'courses': [request.course]}
        )
        mock_api_data_manager(
            module_path='accounts.middleware.thread_local.UserDataManager',
            data={'courses': [request.course]}
        )
        self.get_group_project_for_user_course_mock.return_value = (None, None)

        try:
            infer_page_navigation(request, 'course_id', 'page_id')
        except Exception as exc:
            self.fail("infer_page_navigation raised exception {exception} unexpectedly\n{traceback}".format(
                exception=exc, traceback=traceback.format_exc()
            ))

# TODO: 504 issue fix - uncomment this when original commit is included in release
# class CourseLandingPageTest(TestCase, ApplyPatchMixin, APIDataManagerMockMixin):
#     course_id = u'CS101/ORG101/2018'
#     client_class = AprosTestingClient
#
#     def setUp(self):
#         self.url = reverse('course_landing_page', kwargs={'course_id': self.course_id})
#
#         # Mock checking if user exists in middleware
#         self.mock_get_user_dict = self.apply_patch('accounts.middleware.session_timeout.get_user_dict')
#
#     def test_non_logged_in(self):
#         response = self.client.get(path=self.url)
#
#         # should be a redirect to login page
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(response['Location'], '{}?next={}'.format(reverse('login'), self.url))
#
#     def test_without_access_rights(self):
#         # user is logged-in but is not enrolled to this course
#         self.client.login()
#         self.mock_user_api_data_manager(
#             module_paths=[
#                 'accounts.middleware.thread_local.UserDataManager',
#             ],
#             data={'courses': [], 'current_course': None}
#         )
#
#         response = self.client.get(self.url)
#
#         self.assertEqual(response.status_code, 403)
#
#     @httpretty.activate
#     @mock.patch('courses.views.set_current_course_for_user')
#     def test_with_all_rights(self, mock_set_course):
#         self.client.login()
#         user = auth.get_user(self.client)
#
#         # mock all external calls in the view
#         test_course_data.setup_course_response(self.course_id, user.username)
#         setup_user_courses_response(user_id=user.id)
#         test_course_tabs.setup_course_tabs_response(self.course_id)
#         test_course_metrics_data.setup_course_completions_response(self.course_id)
#         test_course_metrics_data.setup_course_metrics_grades(self.course_id, user_id=user.id)
#         test_course_metrics_data.setup_course_metrics_completions(self.course_id)
#         test_user_grades.setup_user_gradebook_response(self.course_id, user.id)
#         test_user_data.setup_user_profile_response(user.id)
#         user_courses = user_api.get_user_courses(user.id)
#         current_course = user_courses[0]
#
#         self.mock_user_api_data_manager(
#             module_paths=[
#                 'accounts.middleware.thread_local.UserDataManager',
#             ],
#             data={'courses': user_courses, 'current_course': current_course}
#         )
#
#         response = self.client.get(self.url)
#
#         self.assertEqual(response.status_code, 200)
#
#         # ensure page's context has expected data
#         for data in ['course', 'proficiency', 'social', 'graded_items_count']:
#             self.assertIn(data, response.context)
#
#
# class CourseOverviewPageTest(TestCase, ApplyPatchMixin, APIDataManagerMockMixin):
#     course_id = u'CS101/ORG101/2018'
#     client_class = AprosTestingClient
#
#     def setUp(self):
#         self.url = reverse('course_overview', kwargs={'course_id': self.course_id})
#
#         # Mock checking if user exists in middleware
#         self.mock_get_user_dict = self.apply_patch('accounts.middleware.session_timeout.get_user_dict')
#
#     def test_non_logged_in(self):
#         response = self.client.get(path=self.url)
#
#         # should be a redirect to login page
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(response['Location'], '{}?next={}'.format(reverse('login'), self.url))
#
#     def test_without_access_rights(self):
#         self.client.login()
#
#         # user is logged-in but is not enrolled to this course
#         self.mock_user_api_data_manager(
#             module_paths=[
#                 'accounts.middleware.thread_local.UserDataManager',
#             ],
#             data={'courses': [], 'current_course': None}
#         )
#
#         response = self.client.get(self.url)
#
#         self.assertEqual(response.status_code, 403)
#
#     @httpretty.activate
#     def test_get_overview(self):
#         self.client.login()
#         user = auth.get_user(self.client)
#
#         test_course_data.setup_course_overview_response(self.course_id)
#         test_user_data.setup_user_courses_response(user.id)
#
#         user_courses = user_api.get_user_courses(user.id)
#         current_course = user_courses[0]
#         self.mock_user_api_data_manager(
#             module_paths=[
#                 'accounts.middleware.thread_local.UserDataManager',
#             ],
#             data={'courses': user_courses, 'current_course': current_course}
#         )
#
#         response = self.client.get(path=self.url)
#
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('overview', response.context)
#
#         about_section = response.context.get('overview').about
#         self.assertIn('<h2>About This Course</h2>', about_section)
#
#
# @ddt.ddt
# class CourseUserProgressTest(TestCase, ApplyPatchMixin, APIDataManagerMockMixin):
#     course_id = u'CS101/ORG101/2018'
#     client_class = AprosTestingClient
#
#     def setUp(self):
#         self.url = reverse('course_feature_flag', kwargs={'course_id': self.course_id})
#         self.mock_user_api_data_manager(
#             module_paths=[
#                 'accounts.middleware.thread_local.UserDataManager',
#             ],
#             data={'courses': [], 'current_course': None}
#         )
#
#         FeatureFlags.objects.get_or_create(course_id=self.course_id)
#
#         # Mock checking if user exists in middleware
#         self.mock_get_user_dict = self.apply_patch('accounts.middleware.session_timeout.get_user_dict')
#
#     @ddt.data(
#         ('get', True, None, 405),  # GET request should fail
#         ('post', False, None, 302),  # not-logged in call should fail
#         ('post', True, None, 403),  # non-privileged access should fail
#         ('post', True, PERMISSION_GROUPS.COMPANY_ADMIN, 403),  # not-privileged access should fail
#         ('post', True, PERMISSION_GROUPS.INTERNAL_ADMIN, 200),  # right privilege should get us in
#     )
#     @ddt.unpack
#     def test_page_access_checks(self, method, logged_in, user_role, expected_response):
#         if logged_in:
#             self.client.login(user_role=user_role)
#
#         response = self.client.get(self.url) if method == 'get' else self.client.post(self.url)
#         self.assertEqual(response.status_code, expected_response)
