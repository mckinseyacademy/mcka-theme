import mock

from django.contrib import messages
from django.test import TestCase

from accounts.controller import (AssignStudentToProgramResult,
                                 EnrollStudentInCourseResult,
                                 enroll_student_in_course,
                                 has_mobile_ready_course, process_access_key,
                                 append_user_mobile_app_id_cookie)
from accounts.tests.utils import (ApplyPatchMixin, _make_company,
                                  _make_course, _make_program,
                                  _make_user)
from admin.models import AccessKey
from api_client.api_error import ApiError
from django.http.response import HttpResponseBase


class TestProcessAccessKey(TestCase, ApplyPatchMixin):
    """ Tests process_access_key method """
    program = None

    @classmethod
    def setUpClass(cls):
        super(TestProcessAccessKey, cls).setUpClass()
        cls.program = _make_program()

    def setUp(self):
        self.user_api = self.apply_patch('accounts.controller.user_api')
        self.apply_patch(
            'accounts.controller.assign_student_to_program',
            return_value=AssignStudentToProgramResult(self.program, None)
        )
        self.patched_enroll_student_in_course = self.apply_patch('accounts.controller.enroll_student_in_course')
        self.user_api.get_user_organizations = mock.Mock(return_value=[_make_company(1)])

    def test_not_registered_with_company(self):
        user = _make_user()
        key = AccessKey.objects.create(client_id=1, code=1234)
        company = _make_company(1, display_name='Other company')
        self.user_api.get_user_organizations = mock.Mock(return_value=[_make_company(1000)])

        result = process_access_key(user, key, company)
        self.assertIsNone(result.enrolled_in_course_ids)
        self.assertIsNone(result.new_enrollements_course_ids)
        self.assertEqual(len(result.messages), 1)
        message = result.messages[0]
        expected_message = "Access Key {key} is associated with company {company}, " \
                           "but you're not registered with it".format(key=key.code, company=company.display_name)
        self.assertEqual(message[1], expected_message)

    def test_adds_new_enrollment_to_enrolled_courses(self):
        course_id = "Course QWERTY"
        user = _make_user()
        key = AccessKey.objects.create(client_id=1, code=1234, program_id=self.program.id, course_id=course_id)
        company = _make_company(1, display_name='Other company')
        self.patched_enroll_student_in_course.return_value = EnrollStudentInCourseResult(course_id, True, True, None)

        result = process_access_key(user, key, company)
        self.assertEqual(result.enrolled_in_course_ids, [course_id])
        self.assertEqual(result.new_enrollements_course_ids, [course_id])

    def test_adds_existing_enrollment_to_enrolled_courses(self):
        course_id = "Course QWERTY"
        user = _make_user()
        key = AccessKey.objects.create(client_id=1, code=1234, program_id=self.program.id, course_id=course_id)
        company = _make_company(1, display_name='Other company')
        self.patched_enroll_student_in_course.return_value = EnrollStudentInCourseResult(course_id, True, False, None)

        result = process_access_key(user, key, company)
        self.assertEqual(result.enrolled_in_course_ids, [course_id])
        self.assertEqual(result.new_enrollements_course_ids, [])

    def test_skips_course_if_not_enrolled(self):
        course_id = "Course QWERTY"
        user = _make_user()
        key = AccessKey.objects.create(client_id=1, code=1234, program_id=self.program.id, course_id=course_id)
        company = _make_company(1, display_name='Other company')
        self.patched_enroll_student_in_course.return_value = EnrollStudentInCourseResult(
            course_id, False, False, "Message"
        )

        result = process_access_key(user, key, company)
        self.assertEqual(result.enrolled_in_course_ids, [])
        self.assertEqual(result.new_enrollements_course_ids, [])
        self.assertEqual(result.messages, ["Message"])


class TestEnrollStudentInCourse(TestCase, ApplyPatchMixin):
    """ Tests for enroll_student_in_course method """

    def _assert_result(self, result, course_id, expected_message, enrolled, new_enrollement):
        self.assertEqual(result.course_id, course_id)
        self.assertEqual(result.message, expected_message)
        self.assertEqual(result.enrolled, enrolled)
        self.assertEqual(result.new_enrollment, new_enrollement)

    def _make_side_effect_raise_api_error(self, api_error_code):
        thrown_error = mock.Mock()
        thrown_error.code = api_error_code
        thrown_error.reason = "I have no idea, but luckily it is irrelevant for the test"

        def _raise(*args, **kwargs):
            raise ApiError(thrown_error=thrown_error, function_name='irrelevant')

        return _raise

    def setUp(self):
        self.user_api = self.apply_patch('accounts.controller.user_api')

    def test_invalid_course_id(self):
        user = _make_user()
        program = _make_program(courses=[_make_course(course_id_iter) for course_id_iter in [1, 2]])
        course_id = 'qwerty'

        result = enroll_student_in_course(user, program, course_id)
        expected_message = 'Unable to enroll you in course "{}" - it is no longer part of your program.'.format(
            course_id
        )
        self._assert_result(result, course_id, (messages.ERROR, expected_message), False, False)

    def test_new_enrollment(self):
        course_id = 'qwerty'
        user = _make_user()
        program = _make_program(courses=[_make_course(course_id)])

        result = enroll_student_in_course(user, program, course_id)
        expected_message = "Successfully enrolled you in a course {}.".format(course_id)
        self._assert_result(result, course_id, (messages.INFO, expected_message), True, True)

    def test_already_enrolled(self):
        course_id = 'qwerty'
        user = _make_user()
        program = _make_program(courses=[_make_course(course_id)])
        self.user_api.enroll_user_in_course.side_effect = self._make_side_effect_raise_api_error(409)

        result = enroll_student_in_course(user, program, course_id)
        expected_message = 'You are already enrolled in course "{}"'.format(course_id)
        self._assert_result(result, course_id, (messages.INFO, expected_message), True, False)

    def test_failed_to_eroll(self):
        course_id = 'qwerty'
        user = _make_user()
        program = _make_program(courses=[_make_course(course_id)])
        self.user_api.enroll_user_in_course.side_effect = self._make_side_effect_raise_api_error(400)

        result = enroll_student_in_course(user, program, course_id)
        expected_message = 'Unable to enroll you in course "{}".'.format(course_id)
        self._assert_result(result, course_id, (messages.ERROR, expected_message), False, False)


class AccountControllerTest(TestCase, ApplyPatchMixin):
    """
    Test cases for accounts related helper methods
    """

    def setUp(self):
        """
        Sets up the test case
        """
        super(AccountControllerTest, self).setUp()
        self.user_courses_progress_response = [
            {
                "created": "2017-09-13T10:10:52.804706Z",
                "is_active": "true",
                "progress": 0,
                "course": {
                    "end": "null",
                    "mobile_available": "true",
                    "start": "2017-08-01T01:00:00Z",
                    "display_name": "Certificate Demo for OPS",
                    "id": "edx/CS111/2017",
                    "course_image_url": "/c4x/edx/CS111/asset/McKA_course_tile_BusStrat.png"
                }
            }
        ]

        self.get_user_courses_progress = self.apply_patch(
            'accounts.controller.get_user_courses_progress'
        )

    def test_has_mobile_ready_course_with_mobile_ready_courses(self):
        """
        Tests has_mobile_ready_course helper method when user has mobile ready courses
        """
        user_id = 4
        self.get_user_courses_progress.return_value = self.user_courses_progress_response
        self.assertTrue(has_mobile_ready_course(user_id))

    def test_has_mobile_ready_course_without_mobile_ready_courses(self):
        """
        Tests has_mobile_ready_course helper method when user has no mobile ready courses
        """
        user_id = 4
        self.get_user_courses_progress.return_value = []
        self.assertFalse(has_mobile_ready_course(user_id))


class MobileIdAppendInCookieTest(TestCase, ApplyPatchMixin):
    """ Tests for add android and ios user app id in cookie
    """

    def setUp(self):
        """
        Sets up the test case
        """
        super(MobileIdAppendInCookieTest, self).setUp()
        self.ios_app_id = '1234'
        self.android_app_id = '5678'
        self.mobile_app_id = {'ios_app_id': self.ios_app_id, 'android_app_id': self.android_app_id}
        self.user_organizations = [
            {
                "url": "http://0.0.0.0:8000/api/server/organizations/1/",
                "id": 1,
                "name": "mckinsey_and_company",
                "display_name": "McKinsey and Company",
                "contact_name": "McKinsey and Company",
                "contact_email": "company@mckinseyacademy.com",
            }
        ]

        self.get_user_organizations = self.apply_patch(
            'api_client.user_api.get_user_organizations'
        )

        self.get_mobile_apps_id = self.apply_patch(
            'accounts.controller.get_mobile_apps_id'
        )

    def test_has_mobile_apps_id(self):
        """
        Tests append_user_mobile_app_id_cookie helper method when user login and has organization
        """
        user_id = 4
        self.get_user_organizations.return_value = self.user_organizations
        self.get_mobile_apps_id.return_value = self.mobile_app_id

        result = append_user_mobile_app_id_cookie(HttpResponseBase(), user_id)
        self.assertEqual(result.cookies.get('ios_app_id').value, self.ios_app_id)
        self.assertEqual(result.cookies.get('android_app_id').value, self.android_app_id)

    def test_has_not_mobile_apps_id(self):
        """
        Tests append_user_mobile_app_id_cookie helper method when user login and has no organization
        """
        user_id = 4
        self.get_user_organizations.return_value = []
        self.get_mobile_apps_id.return_value = self.mobile_app_id
        result = append_user_mobile_app_id_cookie(HttpResponseBase(), user_id)

        self.assertIsNone(result.cookies.get('ios_app_id'))
        self.assertIsNone(result.cookies.get('android_app_id'))
