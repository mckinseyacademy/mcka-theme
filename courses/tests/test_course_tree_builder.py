import ddt
import httpretty

from django.test import TestCase, Client
from django.utils import translation

from accounts.tests.utils import ApplyPatchMixin
from courses.course_tree_builder import CourseTreeBuilder
from util.unit_test_helpers.test_api_responses import (
    course as test_course_data,
    course_tabs as test_course_tabs,
    user as test_user_data,
    course_metrics as test_course_metrics_data,
    user_grades as test_user_grades
)
from util.unit_test_helpers.common_mocked_objects import TestUser, mock_request_object


@ddt.ddt
class TestCourseTreeBuilder(TestCase, ApplyPatchMixin):
    def setUp(self):
        self.course_id = 'CS101/ORG101/2018'
        self.user = TestUser(user_id=1, email='user@example.com', username='mcka_admin_user')
        self.client = Client()

    @ddt.data(
        ('i4x://a/b/chapter/chapter-1', 'module_xyz'),
        (None, None),
    )
    @ddt.unpack
    def test_initialization(self, lesson_id, module_id):
        """
        Tests if builder is properly initialized
        with expected properties
        """
        if lesson_id and module_id:
            url = '/courses/{}/lessons/{}/module/{}'.format(self.course_id, lesson_id, module_id)
        else:
            url = '/'

        request = self.client.get(path=url)

        tree_builder = CourseTreeBuilder(
            course_id=self.course_id,
            request=request
        )

        self.assertEqual(lesson_id, tree_builder.current_lesson_id)
        self.assertEqual(module_id, tree_builder.current_module_id)

    @httpretty.activate
    def test_load_course(self):
        test_course_data.setup_course_response(self.course_id, self.user.username)

        course_tree_builder = CourseTreeBuilder(course_id=self.course_id, request=None)
        course = course_tree_builder._load_course()

        self.assertGreater(course.chapters, 0)

    @httpretty.activate
    def test_build_page_info(self):
        course_api = self.apply_patch('api_client.course_api')
        course_api.get_users_filtered_by_role.return_value = []
        test_course_data.setup_course_response(self.course_id, self.user.username)

        request = self.client.get(path='/')
        request.user = self.user

        course_tree_builder = CourseTreeBuilder(course_id=self.course_id, request=request)
        course = course_tree_builder._load_course()
        course_tree_builder.build_page_info(course=course)

        self.assertTrue(hasattr(course, 'current_lesson'))

        for idx, lesson in enumerate(course.chapters, start=1):
            self.assertTrue(hasattr(lesson, 'navigation_url'))
            self.assertTrue(hasattr(lesson, 'modules'))

    @httpretty.activate
    def test_include_estimated_completion_times(self):
        course_api = self.apply_patch('api_client.course_api')
        course_api.get_users_filtered_by_role.return_value = []
        test_course_data.setup_course_response(self.course_id, self.user.username)
        test_course_tabs.setup_course_tabs_response(self.course_id)

        request = self.client.get(path='/')
        request.user = self.user

        course_tree_builder = CourseTreeBuilder(course_id=self.course_id, request=request)
        course = course_tree_builder._load_course()

        course_tree_builder.include_estimated_completion_times(course)

        self.assertEqual(course.chapters[0].estimated_time, '<p>est. time 60 min')

    @httpretty.activate
    def test_include_progress_data(self):
        course_api = self.apply_patch('api_client.course_api')
        course_api.get_users_filtered_by_role.return_value = []
        test_user_data.setup_user_profile_response(self.user.id)
        test_course_metrics_data.setup_course_completions_response(self.course_id)

        request = self.client.get(path='/')
        request.user = self.user

        course_tree_builder = CourseTreeBuilder(course_id=self.course_id, request=request)
        course = course_tree_builder._load_course()

        course_tree_builder.include_progress_data(course)

        self.assertTrue(hasattr(course, 'user_progress'))
        self.assertEqual(course.user_progress, 75)

    @httpretty.activate
    def test_include_lesson_descriptions(self):
        course_api = self.apply_patch('api_client.course_api')
        course_api.get_users_filtered_by_role.return_value = []

        test_course_data.setup_course_response(self.course_id, self.user.username)
        test_course_tabs.setup_course_tabs_response(self.course_id)

        request = self.client.get(path='/')
        request.user = self.user

        course_tree_builder = CourseTreeBuilder(course_id=self.course_id, request=request)
        course = course_tree_builder._load_course()

        course_tree_builder.include_lesson_descriptions(course)

        self.assertTrue(hasattr(course.chapters[0], 'description'))

    @httpretty.activate
    @ddt.data(
        # current module is first one, left navigator should be disabled
        (
            'i4x://CS101/ORG101/chapter/01b118e713fa47eb896a3da0ac244bf9',
            'i4x://CS101/ORG101/vertical/6449acfcb3074bfa9630df242dd5b1a4',
            'i4x://CS101/ORG101/vertical/ae8d6e7dd840438391625e5f96b8bb34',
            None,
            'en'
        ),
        # current module is in middle, both left & right navigators are present
        (
            'i4x://CS101/ORG101/chapter/c19dd6d1753d4714917a03d82f03064f',
            'i4x://CS101/ORG101/vertical/5cef8c7ac4dd4782b58de04ade4cd511',
            'i4x://COTORG/COT101/vertical/1c987b91b368472cafb7fd372c294c1f',
            'i4x://CS101/ORG101/vertical/ae8d6e7dd840438391625e5f96b8bb34',
            'en'
        ),
        # current module is last one, right navigator should be disabled
        (
            'i4x://COTORG/COT101/chapter/241059bb81994498938c243d639bf5e0',
            'i4x://COTORG/COT101/vertical/1c987b91b368472cafb7fd372c294c1f',
            None,
            'i4x://CS101/ORG101/vertical/5cef8c7ac4dd4782b58de04ade4cd511',
            'en'
        ),
        # current module is first one with rtl lang, right navigator should be disabled
        (
            'i4x://CS101/ORG101/chapter/01b118e713fa47eb896a3da0ac244bf9',
            'i4x://CS101/ORG101/vertical/6449acfcb3074bfa9630df242dd5b1a4',
            None,
            'i4x://CS101/ORG101/vertical/ae8d6e7dd840438391625e5f96b8bb34',
            'ar'
        ),
    )
    @ddt.unpack
    def test_get_module_navigators(
            self, current_lesson_id, current_module_id,
            right_module_id, left_module_id, lang_code
    ):
        course_api = self.apply_patch('api_client.course_api')
        course_api.get_users_filtered_by_role.return_value = []
        test_course_data.setup_course_response(self.course_id, self.user.username)
        request = mock_request_object(path='/', user=self.user)
        translation.activate(lang_code)

        course_tree_builder = CourseTreeBuilder(course_id=self.course_id, request=request)
        course = course_tree_builder._load_course()

        setattr(course_tree_builder, 'current_lesson_id', current_lesson_id)
        setattr(course_tree_builder, 'current_module_id', current_module_id)

        course_tree_builder.build_page_info(course=course)

        (right_lesson_module_navigator,
         left_lesson_module_navigator) = course_tree_builder.get_module_navigators(course)

        self.assertEqual(
            getattr(right_lesson_module_navigator, 'id', None),
            right_module_id
        )

        self.assertEqual(
            getattr(left_lesson_module_navigator, 'id', None),
            left_module_id
        )

    @httpretty.activate
    def test_get_graded_items_count(self):
        course_api = self.apply_patch('api_client.course_api')
        course_api.get_users_filtered_by_role.return_value = []
        test_user_grades.setup_user_gradebook_response(self.course_id, self.user.id)
        request = mock_request_object(path='/', user=self.user)

        course_tree_builder = CourseTreeBuilder(course_id=self.course_id, request=request)
        course = course_tree_builder._load_course()

        self.assertEqual(course_tree_builder.get_graded_items_count(course), 1)

    @httpretty.activate
    def test_get_processed_course_static_data(self):
        course_api = self.apply_patch('api_client.course_api')
        course_api.get_users_filtered_by_role.return_value = []
        test_course_data.setup_course_response(self.course_id, self.user.username)
        test_course_tabs.setup_course_tabs_response(self.course_id)

        request = mock_request_object(path='/', user=self.user)
        course_tree_builder = CourseTreeBuilder(course_id=self.course_id, request=request)

        course = course_tree_builder.get_processed_course_static_data()

        self.assertEqual(course.chapters[0].estimated_time, '<p>est. time 60 min')
        self.assertTrue(hasattr(course.chapters[0], 'description'))

        # ensure dynamic data is not added
        self.assertFalse(hasattr(course, 'user_progress'))
        self.assertFalse(hasattr(course, 'current_lesson'))

    @httpretty.activate
    def test_get_processed_course_dynamic_data(self):
        course_api = self.apply_patch('api_client.course_api')
        course_api.get_users_filtered_by_role.return_value = []
        test_course_data.setup_course_response(self.course_id, self.user.username)
        test_course_metrics_data.setup_course_completions_response(self.course_id)
        test_user_data.setup_user_profile_response(self.user.id)

        request = mock_request_object(path='/', user=self.user)
        course_tree_builder = CourseTreeBuilder(course_id=self.course_id, request=request)
        course = course_tree_builder._load_course()

        course = course_tree_builder.get_processed_course_dynamic_data(course)

        self.assertTrue(hasattr(course, 'user_progress'))
        self.assertTrue(hasattr(course, 'current_lesson'))

        self.assertFalse(hasattr(course.chapters[0], 'estimated_time'))
        self.assertFalse(hasattr(course.chapters[0], 'description'))
