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
            module_path='courses.user_courses.UserDataManager',
            data={'courses': [request.course]}
        )
        mock_api_data_manager(
            module_path='courses.views.UserDataManager',
            data={'courses': [request.course]}
        )
        self.get_group_project_for_user_course_mock.return_value = (None, None)

        try:
            infer_page_navigation(request, 'course_id', 'page_id')
        except Exception as exc:
            self.fail("infer_page_navigation raised exception {exception} unexpectedly\n{traceback}".format(
                exception=exc, traceback=traceback.format_exc()
            ))

