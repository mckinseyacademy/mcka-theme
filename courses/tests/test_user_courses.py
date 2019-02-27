import ddt
import mock
from collections import defaultdict

from django.test import TestCase, override_settings
from django.conf import settings
from django.http.response import HttpResponseBase

from accounts.tests.utils import ApplyPatchMixin, make_course, make_program
from api_data_manager.tests.utils import mock_api_data_manager
from courses.user_courses import (
    set_current_course_for_user,
    standard_data,
    get_program_menu_list,
    check_course_shell_access,
    CourseAccessDeniedError,
    CompanyAdminAccessDeniedError
)
from lib.utils import DottableDict
from api_client import course_models


class TestSetCurrentCourseForUser(TestCase, ApplyPatchMixin):
    """
    Test for set_current_course_for_user method
    """
    def get_user_groups(self, user_id, **kwargs):
        if user_id:
            user_programs = self.programs[:2]
            course_id = kwargs.get('course', None)
            if course_id is not None:
                user_programs = [program for program in user_programs for course in program.courses
                                 if course.course_id == course_id]
            return user_programs

    def set_user_preferences(self, user_id, preference_dictionary):
        self.user_id = user_id
        self.preference_dictionary = preference_dictionary

    def setUp(self):
        self.request = mock.Mock()
        self.request.user.id = 1

        courses = [
            {
                "id": "Organization_X/CS103/2018_T3",
                "name": "Cycling to Work",
            },
            {
                "id": "Organization_y/CS105/2018_T5",
                "name": "Walking",
            },
            {
                "id": "Organization_z/CS107/2018_T7",
                "name": "Trains and Buses",
            }
        ]
        self.courses = [make_course(course_id=course['id'], display_name=course['name']) for course in courses]
        self.programs = [make_program(prog_id=i, display_name='Test program {}'.format(i), courses=[course])
                         for i, course in enumerate(self.courses)]

        program_courses_mapping = defaultdict(dict)
        for program in self.programs:
            program_courses_mapping[program.id] = {'name': program.display_name, 'courses': program.courses}
        self.programs[0].courses[0].id = self.programs[0].courses[0].course_id

        self.user_api = self.apply_patch('admin.models.user_api.get_user_groups', self.get_user_groups)
        self.get_cached_data = self.apply_patch('courses.user_courses.CommonDataManager.get_cached_data')
        self.apply_patch('courses.user_courses.user_api.set_user_preferences', self.set_user_preferences)
        self.get_cached_data.return_value = program_courses_mapping

    def test_set_current_course_for_user(self):
        mock_api_data_manager(
            module_path='courses.user_courses.UserDataManager',
            data={'current_course': self.programs[0].courses[0],
                  'current_program': self.programs[0],
                  }
        )
        set_current_course_for_user(self.request, 'Organization_y/CS105/2018_T5')
        self.assertEqual(self.user_id, 1)
        self.assertEqual(self.preference_dictionary['current_program_id'], '1')
        self.assertEqual(self.preference_dictionary['current_course_id'], 'Organization_y/CS105/2018_T5')

    def test_set_current_course_for_user_with_program_courses_mapping_none(self):
        mock_api_data_manager(
            module_path='courses.user_courses.UserDataManager',
            data={'current_course': self.programs[0].courses[0],
                  'current_program': self.programs[0],
                  }
        )
        self.get_cached_data.return_value = None
        set_current_course_for_user(self.request, 'Organization_y/CS105/2018_T5')
        self.assertEqual(self.user_id, 1)
        self.assertEqual(self.preference_dictionary['current_program_id'], '1')
        self.assertEqual(self.preference_dictionary['current_course_id'], 'Organization_y/CS105/2018_T5')


@ddt.ddt
class TestCourseAccessDeniedError(TestCase):
    """
    Test CourseAccessDeniedError class from courses/user_courses.py
    """
    @ddt.data(
        ('course_id', 1),
        (u'course_id', 1),
    )
    @ddt.unpack
    def test_course_access_denied_error(self, course_id, user_id):
        error = CourseAccessDeniedError(course_id, user_id)
        self.assertEquals(error.course_id, 'course_id')
        self.assertEquals(error.user_id, 1)
        self.assertEquals(error.__str__(), "Access denied to course 'course_id' for user 1")
        self.assertEquals(error.__unicode__(), u"Access denied to course 'course_id' for user 1")


class TestCompanyAdminAccessDeniedError(TestCase):
    """
    Test CompanyAdminAccessDeniedError class from courses/user_courses.py
    """
    def setUp(self):
        self.request = mock.Mock()
        self.request.user.id = 1

    def test_company_admin_access_denied_error_str(self):
        user_id = 3
        error = CompanyAdminAccessDeniedError(user_id, self.request.user.id)
        self.assertEquals(error.admin_user_id, 1)
        self.assertEquals(error.user_id, 3)
        self.assertEquals(error.__str__(), "Access denied to user 1 for data belonging to 3")
        self.assertEquals(error.__unicode__(), u"Access denied to user 1 for data belonging to 3")


class TestStandardData(TestCase, ApplyPatchMixin):
    """
    Unit test for standard_data method
    """
    def setUp(self):
        self.request = mock.Mock()
        self.request.user.id = 1
        self.request.resolver_match.kwargs.get = lambda _: None

        self.course_name = "MckinseyMckinseyMckinseyMckinseyMckinseyMckinseyMckinseyMckinsey"
        course = {
            "id": "Organization_X/CS103/2018_T3",
            "name": self.course_name,
            "is_active": True,
        }
        self.course = course_models.Course(dictionary=course)
        self.program = make_program(prog_id=1, display_name='Test program', courses=[self.course])

        self.get_mobile_apps = \
            self.apply_patch('api_data_manager.organization_data.get_mobile_apps')
        self.get_mobile_apps.return_value = {}

    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
    def test_standard_data(self):
        self.user_organizations = [
            DottableDict(
                url="http://0.0.0.0:8000/api/server/organizations/1/",
                id=1,
                name="mckinsey_and_company",
                display_name="McKinsey and Company",
                contact_name="McKinsey and Company",
                contact_email="company@mckinseyacademy.com",
            )
        ]
        mock_api_data_manager(
            module_path='courses.user_courses.UserDataManager',
            data={'courses': [self.course],
                  'current_course': self.course,
                  'current_program': self.program,
                  'organizations': self.user_organizations}
        )

        result = standard_data(self.request)
        self.assertEqual(result['current_course'].id, 'Organization_X/CS103/2018_T3')
        self.assertEqual(result['program'].display_name, 'Test program')
        self.assertEqual(len(result['program'].courses), 1)
        self.assertEqual(result['program'].courses[0], self.course)
        self.assertEqual(result['feature_flags'].course_id, 'Organization_X/CS103/2018_T3')
        self.assertEqual(result['namespace'], 'Organization_X/CS103/2018_T3')
        self.assertNotEqual(result['course_name'], self.course_name)
        self.assertEqual(result['client_customization'], None)
        self.assertEqual(result['client_nav_links'], {})
        self.assertEqual(result['branding'], None)
        self.assertEqual(result['organization_id'], 1)
        self.assertEqual(result['lesson_custom_label'], '')
        self.assertEqual(result['module_custom_label'], '')
        self.assertEqual(result['lessons_custom_label'], '')
        self.assertEqual(result['modules_custom_label'], '')


class TestGetProgramMenuList(TestCase, ApplyPatchMixin):
    """
    Unit test for the method get_program_menu_list
    """
    def setUp(self):
        self.request = mock.Mock()
        self.request.user.id = 1

        users_courses = [
            {
                "id": "Organization_X/CS103/2018_T3",
                "name": "Essential Principles Of Business",
                "is_active": True
            },
            {
                "id": "Organization_Y/CS105/2018_T5",
                "name": "An Integrated Approach To Business Studies",
                "is_active": True
            }
        ]
        self.users_courses = [course_models.Course(dictionary=course) for course in users_courses]
        self.users_courses[0].course_id = 'Organization_X/CS103/2018_T3'
        self.program = make_program(prog_id=1, display_name='Business Strategy Program',
                                    courses=[self.users_courses[0]])

        self.get_user_courses = self.apply_patch('courses.user_courses.user_api.get_user_courses')
        self.user_api = self.apply_patch('admin.models.user_api')
        self.group_api = self.apply_patch('admin.models.group_api')
        self.organization_api = self.apply_patch('courses.user_courses.organization_api')
        self.get_mobile_apps = self.apply_patch('api_client.mobileapp_api.get_mobile_apps')

    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
    def test_get_program_menu_list(self):
        mock_api_data_manager(
            module_path='courses.user_courses.UserDataManager',
            data={'courses': self.users_courses,
                  'current_course': self.users_courses[0],
                  }
        )

        self.user_api.get_user_groups.return_value = [self.program]
        self.get_user_courses.return_value = self.users_courses
        self.get_mobile_apps.return_value = DottableDict(
            {'results': [{'name': 'demo',
                          'deployment_mechanism': 1,
                          'ios_app_id': 1,
                          'organizations': [1],
                          'android_app_id': 2}]
             })

        companion_app_course = DottableDict(
            {'id': 'Organization_Z/CS107/2018_T7',
             'started': True,
             'name': 'An Introduction to business',
             'mobile_available': True,
             })
        self.organization_api.get_organizations_courses.return_value = [companion_app_course]
        self.group_api.get_courses_in_group.return_value = [self.users_courses[0]]

        programs = get_program_menu_list(self.request)
        self.assertEqual(programs[0][0].id, 1)
        self.assertEqual(programs[0][0].display_name, 'Business Strategy Program')
        self.assertEqual(programs[0][1][0].id, 'Organization_X/CS103/2018_T3')
        self.assertEqual(programs[0][1][0].name, 'Essential Principles Of Business')
        self.assertEqual(programs[0][1][0].course_class, 'current')

        # check current course
        self.assertEqual(programs[0][1][0], self.program.courses[0])

        self.assertEqual(programs[1][0].id, 'NO_PROGRAM')
        self.assertEqual(programs[1][0].display_name, settings.NO_PROGRAM_NAME)
        self.assertEqual(programs[1][1][0].id, 'Organization_Y/CS105/2018_T5')
        self.assertEqual(programs[1][1][0].name, 'An Integrated Approach To Business Studies')

        # check companion app courses, should not be in program menu list
        for program in programs:
            self.assertNotEqual(program[1][0].id, companion_app_course.id)


class TestCheckCourseShellAccess(TestCase, ApplyPatchMixin):
    """
    test for the method check_course_shell_access
    """
    def _request_mock(self, user_id, course_id):
        request_mock = mock.Mock()
        request_mock.user.id = user_id

        course_mock = mock.Mock()
        course_mock.id = course_id
        course_mock.started = True
        request_mock.course = course_mock

        request_mock.session = {'last_visited_course': course_mock.id}
        return request_mock

    def setUp(self):
        self.user_api = self.apply_patch('courses.user_courses.user_api')

    def test_check_course_shell_access(self):
        request = self._request_mock(1, 'course_id')
        self.user_api.get_user_courses.return_value = [request.course]
        check_course_shell_access(request, 'course_id')

    def test_check_course_shell_no_access(self):
        request = self._request_mock(1, 'course_id')
        self.user_api.get_user_courses.return_value = [request.course]
        self.user_api.delete_user_preference.return_value = HttpResponseBase(status=204)
        with self.assertRaises(CourseAccessDeniedError):
            check_course_shell_access(request, 'id')
