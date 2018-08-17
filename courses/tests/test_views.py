import traceback
import mock
from django.test import TestCase, RequestFactory
from lib.utils import DottableDict
from courses.models import FeatureFlags
from courses.user_courses import CURRENT_PROGRAM
from courses.views import infer_page_navigation, get_feature_flag_mobile
from accounts.tests.utils import ApplyPatchMixin


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

    def test_infer_page_navigation_no_group_work_does_not_crash(self):
        request = self._get_request_mock(1, 'course_id')
        self.get_group_project_for_user_course_mock.return_value = (None, None)

        try:
            infer_page_navigation(request, 'course_id', 'page_id')
        except Exception as exc:
            self.fail("infer_page_navigation raised exception {exception} unexpectedly\n{traceback}".format(
                exception=exc, traceback=traceback.format_exc()
            ))


class MobileFeatureFlagAccessTest(TestCase, ApplyPatchMixin):

    def setUp(self):
        self.response = {"id": 7}
        self.status_code = 200
        self.factory = RequestFactory()
        get_user_by_bearer_token = 'api_client.user_api.get_user_by_bearer_token'
        self.get_user_by_bearer_token = self.apply_patch(get_user_by_bearer_token)

    def test_user_single_feature_flag_access(self):

        course_id = '1st-course'
        request = self.factory.get('/courses/1st-course/feature_flag', HTTP_AUTHORIZATION='Bearer token')
        get_user_by_bearer_token = self.get_user_by_bearer_token
        get_user_by_bearer_token.return_value = self.response, self.status_code
        FeatureFlags.objects.create(
            course_id=course_id,
        )
        course_participants = get_feature_flag_mobile(request, course_id)
        self.assertEqual(course_participants.status_code, 200)

    def test_user_all_courses_feature_flag_access(self):

        request = self.factory.get('/courses/feature_flag', HTTP_AUTHORIZATION='Bearer token')
        get_user_by_bearer_token = self.get_user_by_bearer_token
        get_user_by_bearer_token.return_value = self.response, self.status_code
        course = [
            DottableDict({'id': '1st-course'}),
            DottableDict({'id': '2nd-course'}),
        ]
        FeatureFlags.objects.create(
            course_id="1st-course",
        )
        FeatureFlags.objects.create(
            course_id="2nd-course",
        )

        get_user_courses = 'api_client.user_api.get_user_courses'
        get_user_courses = self.apply_patch(get_user_courses)
        get_user_courses.return_value = course
        course_participants = get_feature_flag_mobile(request)
        self.assertEqual(course_participants.status_code, 200)

