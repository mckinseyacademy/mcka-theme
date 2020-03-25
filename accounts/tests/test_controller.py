import datetime
import json
import ddt
import mock

from django.contrib import messages
from django.core import mail
from django.core.files.storage import default_storage
from django.http.response import HttpResponseBase
from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from accounts.controller import (AssignStudentToProgramResult, EnrollStudentInCourseResult,
                                 enroll_student_in_course, process_access_key, ActivationError,
                                 enroll_student_in_course_without_program, append_user_mobile_app_id_cookie,
                                 assign_student_to_program, is_future_start, send_warning_email_to_admin,
                                 send_email, send_password_reset_email, user_activation_with_data,
                                 io_new_client_image, save_new_client_image, get_mobile_apps_id,
                                 get_sso_provider, _set_number_of_enrolled_users, ExistingSelfRegistration,
                                 NewSelfRegistration, MckaUserSelfregistration,
                                 process_registration_request, _process_course_run_closed)
from accounts.models import UserActivation
from accounts.tests.utils import (ApplyPatchMixin, make_company,
                                  make_course, make_program,
                                  make_user, make_side_effect_raise_api_error, delete_files, AccessKeyTestBase)
from admin.models import AccessKey, CourseRun, Client
from api_client.api_error import ApiError
from api_client.organization_models import Organization
from lib.utils import DottableDict
from license.models import LicenseGrant
from mcka_apros import settings


class TestProcessAccessKey(AccessKeyTestBase):
    """ Tests process_access_key method """

    def test_not_registered_with_company(self):
        user = make_user()
        key = AccessKey.objects.create(client_id=1, code=1234)
        company = make_company(1, display_name='Other company')
        self.user_api.get_user_organizations = mock.Mock(return_value=[make_company(1000)])

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
        user = make_user()
        key = AccessKey.objects.create(client_id=1, code=1234, program_id=self.program.id, course_id=course_id)
        company = make_company(1, display_name='Other company')
        self.patched_enroll_student_in_course.return_value = EnrollStudentInCourseResult(course_id, True, True, None)

        result = process_access_key(user, key, company)
        self.assertEqual(result.enrolled_in_course_ids, [course_id])
        self.assertEqual(result.new_enrollements_course_ids, [course_id])

    def test_adds_existing_enrollment_to_enrolled_courses(self):
        course_id = "Course QWERTY"
        user = make_user()
        key = AccessKey.objects.create(client_id=1, code=1234, program_id=self.program.id, course_id=course_id)
        company = make_company(1, display_name='Other company')
        self.patched_enroll_student_in_course.return_value = EnrollStudentInCourseResult(course_id, True, False, None)

        result = process_access_key(user, key, company)
        self.assertEqual(result.enrolled_in_course_ids, [course_id])
        self.assertEqual(result.new_enrollements_course_ids, [])

    def test_skips_course_if_not_enrolled(self):
        course_id = "Course QWERTY"
        user = make_user()
        key = AccessKey.objects.create(client_id=1, code=1234, program_id=self.program.id, course_id=course_id)
        company = make_company(1, display_name='Other company')
        self.patched_enroll_student_in_course.return_value = EnrollStudentInCourseResult(
            course_id, False, False, "Message"
        )

        result = process_access_key(user, key, company)
        self.assertEqual(result.enrolled_in_course_ids, [])
        self.assertEqual(result.new_enrollements_course_ids, [])
        self.assertEqual(result.messages, ["Message"])


class TestEnrollStudentInCourseWithoutProgram(TestCase, ApplyPatchMixin):
    """ Tests for enroll_student_in_course_without_program method """

    def _assert_result(self, result, expected_result):
        self.assertEqual(result.course_id, expected_result.course_id)
        self.assertEqual(result.message, expected_result.expected_message)
        self.assertEqual(result.enrolled, expected_result.enrolled)
        self.assertEqual(result.new_enrollment, expected_result.new_enrollment)

    def setUp(self):
        self.user_api = self.apply_patch('accounts.controller.user_api')

    def test_invalid_course_id(self):
        user = make_user()
        make_course(1)
        course_id = 'qwerty_invalid'
        self.user_api.enroll_user_in_course.side_effect = make_side_effect_raise_api_error(404)

        result = enroll_student_in_course_without_program(user, course_id)
        expected_message = 'Unable to enroll you in course "{}".'.format(
            course_id
        )
        expected_result = DottableDict({'course_id': course_id,
                                        'expected_message': (messages.ERROR, expected_message),
                                        'enrolled': False,
                                        'new_enrollment': False})
        self._assert_result(result, expected_result)

    def test_new_enrollment(self):
        course_id = 'qwerty'
        user = make_user()
        make_course(course_id)

        result = enroll_student_in_course_without_program(user, course_id)
        expected_message = "Successfully enrolled you in a course {}.".format(course_id)
        expected_result = DottableDict({'course_id': course_id,
                                        'expected_message': (messages.INFO, expected_message),
                                        'enrolled': True,
                                        'new_enrollment': True})
        self._assert_result(result, expected_result)

    def test_already_enrolled(self):
        course_id = 'qwerty'
        user = make_user()
        make_course(course_id)
        self.user_api.enroll_user_in_course.side_effect = make_side_effect_raise_api_error(409)

        result = enroll_student_in_course_without_program(user, course_id)
        expected_result = DottableDict({'course_id': course_id,
                                        'expected_message': None,
                                        'enrolled': True,
                                        'new_enrollment': False})
        self._assert_result(result, expected_result)

    def test_failed_to_enroll(self):
        course_id = 'qwerty'
        user = make_user()
        make_course(course_id)
        self.user_api.enroll_user_in_course.side_effect = make_side_effect_raise_api_error(400)

        result = enroll_student_in_course_without_program(user, course_id)
        expected_message = 'Unable to enroll you in course "{}".'.format(course_id)
        expected_result = DottableDict({'course_id': course_id,
                                        'expected_message': (messages.ERROR, expected_message),
                                        'enrolled': False,
                                        'new_enrollment': False})
        self._assert_result(result, expected_result)


class TestEnrollStudentInCourse(TestCase, ApplyPatchMixin):
    """ Tests for enroll_student_in_course method """

    def _assert_result(self, result, expected_result):
        self.assertEqual(result.course_id, expected_result.course_id)
        self.assertEqual(result.message, expected_result.expected_message)
        self.assertEqual(result.enrolled, expected_result.enrolled)
        self.assertEqual(result.new_enrollment, expected_result.new_enrollment)

        def _raise(*args, **kwargs):
            # TODO thrown_error undefined
            raise ApiError(thrown_error=thrown_error, function_name='irrelevant')  # noqa: F821

        return _raise

    def setUp(self):
        self.user_api = self.apply_patch('accounts.controller.user_api')

    def test_invalid_course_id(self):
        user = make_user()
        program = make_program(courses=[make_course(1)])
        course_id = 'qwerty'

        result = enroll_student_in_course(user, program, course_id)
        expected_message = 'Unable to enroll you in course "{}" - it is no longer part of your program.'.format(
            course_id
        )
        expected_result = DottableDict({'course_id': course_id,
                                        'expected_message': (messages.ERROR, expected_message),
                                        'enrolled': False,
                                        'new_enrollment': False})
        self._assert_result(result, expected_result)

    def test_new_enrollment(self):
        course_id = 'qwerty'
        user = make_user()
        program = make_program(courses=[make_course(course_id)])

        result = enroll_student_in_course(user, program, course_id)
        expected_message = "Successfully enrolled you in a course {}.".format(course_id)
        expected_result = DottableDict({'course_id': course_id,
                                        'expected_message': (messages.INFO, expected_message),
                                        'enrolled': True,
                                        'new_enrollment': True})
        self._assert_result(result, expected_result)

    def test_already_enrolled(self):
        course_id = 'qwerty'
        user = make_user()
        program = make_program(courses=[make_course(course_id)])
        self.user_api.enroll_user_in_course.side_effect = make_side_effect_raise_api_error(409)

        result = enroll_student_in_course(user, program, course_id)
        expected_result = DottableDict({'course_id': course_id,
                                        'expected_message': None,
                                        'enrolled': True,
                                        'new_enrollment': False})
        self._assert_result(result, expected_result)

    def test_failed_to_enroll(self):
        course_id = 'qwerty'
        user = make_user()
        program = make_program(courses=[make_course(course_id)])
        self.user_api.enroll_user_in_course.side_effect = make_side_effect_raise_api_error(400)

        result = enroll_student_in_course(user, program, course_id)
        expected_message = 'Unable to enroll you in course "{}".'.format(course_id)
        expected_result = DottableDict({'course_id': course_id,
                                        'expected_message': (messages.ERROR, expected_message),
                                        'enrolled': False,
                                        'new_enrollment': False})
        self._assert_result(result, expected_result)


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
            DottableDict(
                url="http://0.0.0.0:8000/api/server/organizations/1/",
                id=17,
                name="mckinsey_and_company",
                display_name="McKinsey and Company",
                contact_name="McKinsey and Company",
                contact_email="company@mckinseyacademy.com",
            )
        ]

        self.get_mobile_apps_id = self.apply_patch(
            'accounts.controller.get_mobile_apps_id'
        )

    def test_has_mobile_apps_id(self):
        """
        Tests append_user_mobile_app_id_cookie helper method when user login and has organization
        """
        user_id = 4
        self.get_basic_user_data = self.apply_patch('accounts.controller.thread_local.get_basic_user_data')
        self.get_basic_user_data.return_value = DottableDict({
            'organization': self.user_organizations[0]
        })
        self.get_mobile_apps_id.return_value = self.mobile_app_id

        result = append_user_mobile_app_id_cookie(HttpResponseBase(), user_id)
        self.assertEqual(result.cookies.get('ios_app_id').value, self.ios_app_id)
        self.assertEqual(result.cookies.get('android_app_id').value, self.android_app_id)
        self.assertEqual(result.cookies.get('user_organization_id').value, str(self.user_organizations[0].id))

    def test_has_not_mobile_apps_id(self):
        """
        Tests append_user_mobile_app_id_cookie helper method when user login and has no organization
        """
        user_id = 4
        self.get_basic_user_data = self.apply_patch('courses.user_courses.thread_local.get_basic_user_data')
        self.get_basic_user_data.return_value = DottableDict({
            'organization': []
        })
        self.get_mobile_apps_id.return_value = self.mobile_app_id
        result = append_user_mobile_app_id_cookie(HttpResponseBase(), user_id)

        self.assertIsNone(result.cookies.get('ios_app_id'))
        self.assertIsNone(result.cookies.get('android_app_id'))


class TestNewSelfRegistration(TestCase, ApplyPatchMixin):

    def setUp(self):
        self.user_api = self.apply_patch('accounts.controller.user_api')
        self.user = DottableDict({
            'id': 1,
            'first_name': 'Test',
            'last_name': 'Test',
            'username': 'test',
            'company_email': 'user@arbisoft.com',
            'email': 'test@test.com'
        })
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.organization = Organization()
        self.organization._user_ids.append(1)
        setattr(self.organization, 'id', 1)
        self.organization_api = self.apply_patch('accounts.controller.organization_api')
        self.client_api = self.apply_patch('api_client.organization_models.organization_api')
        self.client_api.fetch_organization.return_value = self.organization
        self.client_api.add_user_to_organization.return_value = HttpResponseBase(status=200)

    def test_register_user_on_platform_with_valid_input(self):
        self.user_api.register_user.return_value = HttpResponseBase(status=200)
        self.assertEqual(NewSelfRegistration._register_user_on_platform(self.user).status_code, 200)

    def test_register_user_on_platform_with_invalid_input(self):
        self.user_api.register_user.return_value = ValueError('Api error')
        self.assertEqual(str(NewSelfRegistration._register_user_on_platform(self.user)), 'Api error')

    def test_generate_activation_link(self):
        link = NewSelfRegistration.generate_activation_link(self.request, self.user)
        expected_link = UserActivation.get_user_activation(self.user).activation_key
        expected_output = 'http://testserver/accounts/activate/{}/activation/'.format(expected_link)
        self.assertEqual(link, expected_output)

    def test_get_set_company_with_existing_company(self):
        self.organization_api.get_organization_by_display_name.return_value = {'count': 1, 'results': [{'id': 1}]}
        user_ids = self.organization.users
        self.assertEqual(len(user_ids), 1)
        NewSelfRegistration._get_set_company(2)
        user_ids = self.organization.users
        self.assertEqual(len(user_ids), 2)

    def test_get_set_company_with_new_company(self):
        self.organization_api.get_organization_by_display_name.return_value = {'count': 0}
        self.organization_api.create_organization.return_value = DottableDict({'id': 1})
        user_ids = self.organization.users
        self.assertEqual(len(user_ids), 1)
        NewSelfRegistration._get_set_company(3)
        user_ids = self.organization.users
        self.assertEqual(len(user_ids), 2)


@ddt.ddt
class SelfRegistrationTest(TestCase, ApplyPatchMixin):
    generate_activation_link = "https://www.testlink.com"
    inactive_user = DottableDict(id=1, email="inactive@test.com", first_name="test", last_name="test", mcka_user=False,
                                 company_email="inacvtive@test.com", is_active=False, new_user=False)
    active_user = DottableDict(id=1, email="active@test.com", first_name="test", last_name="test", mcka_user=False,
                               company_email="active@test.com", is_active=True, new_user=False)
    new_user = DottableDict(id=1, email="new@test.com", first_name="test", last_name="test", mcka_user=False,
                            company_email="new@test.com", new_user=True, is_active=False)
    mcka_user = DottableDict(id=1, email="mcka@test.com", first_name="test", last_name="test", mcka_user=True,
                             company_email="mcka@test.com", new_user=False, is_active=False)

    def setUp(self):
        super(SelfRegistrationTest, self).setUp()
        request_factory = RequestFactory()
        self.request = request_factory.get('http://apros.mcka.local/registration/test/')
        self.request.META = {'HTTP_HOST': 'apros.mcka.local'}

        self.course_run = CourseRun.objects.create(
            name="test_course", course_id="test", email_template_new="new", email_template_existing="existing",
            email_template_mcka="mcka", email_template_closed="closed", self_registration_page_heading="test_heading",
            self_registration_description_text="test description"
        )

        self.enroll_without_program = self.apply_patch('accounts.controller.enroll_student_in_course_without_program')
        self.enroll_without_program.return_value = DottableDict(enrolled=True)

        self.register_user_on_platform = self.apply_patch(
            'accounts.controller.NewSelfRegistration._register_user_on_platform')

        self.enroll_user_in_course = self.apply_patch('accounts.controller.enroll_user_in_course')
        self.apply_patch('accounts.controller.NewSelfRegistration._get_set_company')

    @ddt.data(
        (new_user, None, False),
        (inactive_user, inactive_user, True),
        (active_user, active_user, True),
        (mcka_user, mcka_user, True)
    )
    @ddt.unpack
    def test_process_registration_request(self, user, existing_user, success):
        process_registration_request(self.request, user, self.course_run, existing_user)
        result = user.email in [email.to[0] for email in mail.outbox]
        self.assertEqual(result, success)

    @ddt.data(
        (None, generate_activation_link, False, False),
        (inactive_user, generate_activation_link, False, True),
        (active_user, generate_activation_link, False, False),
        (inactive_user, None, ValueError, False),
    )
    @ddt.unpack
    def test_new_user_registration(self, registration_request, generate_activation_link, exception, success):
        self.register_user_on_platform.return_value = registration_request

        generate_link = self.apply_patch('accounts.controller.NewSelfRegistration.generate_activation_link')
        generate_link.return_value = generate_activation_link

        if exception:
            with self.assertRaises(exception):
                NewSelfRegistration.process_registration(self.request, registration_request,
                                                         self.course_run)
        else:
            NewSelfRegistration.process_registration(self.request, registration_request, self.course_run)

        if registration_request:
            result = registration_request.email in [email.to[0] for email in mail.outbox]
            self.assertEqual(result, success)

    @ddt.data(
        (active_user, DottableDict(enrolled=True), False, True),
        (active_user, DottableDict(enrolled=False), ValueError, False),
    )
    @ddt.unpack
    def test_existing_user_registration(self, registration_request, enroll_without_program, exception, success):

        self.enroll_without_program.return_value = enroll_without_program
        if exception:
            with self.assertRaises(exception):
                ExistingSelfRegistration.process_registration(self.request, registration_request,
                                                              self.course_run, registration_request)

        else:
            ExistingSelfRegistration.process_registration(self.request, registration_request,
                                                          self.course_run, registration_request)

        result = registration_request.email in [email.to[0] for email in mail.outbox]
        self.assertEqual(result, success)

    @ddt.data(
        (mcka_user, DottableDict(enrolled=True), False, True),
        (active_user, DottableDict(enrolled=False), ValueError, False),
    )
    @ddt.unpack
    def test_mcka_user_registration(self, registration_request, enroll_without_program, exception, success):
        self.enroll_without_program.return_value = enroll_without_program
        if exception:
            with self.assertRaises(exception):
                MckaUserSelfregistration.process_registration(self.request, registration_request,
                                                              self.course_run, registration_request)

        else:
            MckaUserSelfregistration.process_registration(self.request, registration_request,
                                                          self.course_run, registration_request)

        result = registration_request.email in [email.to[0] for email in mail.outbox]
        self.assertEqual(result, success)

    def test_process_course_run_closed(self):
        _process_course_run_closed(self.new_user, self.course_run)
        self.assertEqual(mail.outbox[0].to[0], self.new_user.email)
        self.assertEqual(mail.outbox[0].from_email, 'support@mckinsey.com')
        self.assertEqual(mail.outbox[0].subject, 'Your request to access McKinsey Academy')


class TestActivationError(TestCase):
    """ Test ActivationError class from accounts/controller.py"""

    def test_activation_error_str(self):
        exception_message = 'test'
        error_code = 'invalid'
        error = ActivationError(exception_message, error_code)
        self.assertEqual(error.value, 'test')
        self.assertEqual(error.error_code, 'invalid')
        self.assertEqual(error.__str__(), "ActivationError 'test'")


class TestAssignStudentToProgram(TestCase, ApplyPatchMixin):
    ''' Unit test for the method assign_student_to_program from controller'''

    def setUp(self):
        self.user = DottableDict({"id": 1})
        self.client = DottableDict({"id": 1})
        self.program_id = 1
        self.courses = make_course(1)
        self.program = make_program(
            prog_id=1,
            courses=self.courses
        )
        self.group_api = self.apply_patch('api_client.group_models.group_api')
        self.group_api_course = self.apply_patch('admin.models.group_api')
        self.user_api = self.apply_patch('admin.models.user_api')
        self.license_grant = LicenseGrant(granted_id=1, grantor_id=1)
        self.group_api.fetch_group.return_value = self.program
        self.group_api_course.get_courses_in_group.return_value = self.courses

    def test_with_unoccupied_program(self):
        self.user_api.get_user_groups.return_value = [1]
        self.license_grant.grantee_id = None
        self.license_grant.save()
        result = assign_student_to_program(self.user, self.client, self.program_id)
        self.assertEqual(result, AssignStudentToProgramResult(self.program, None))

    def test_with_already_full_program(self):
        self.license_grant.grantee_id = 2
        self.group_api.fetch_group.return_value = self.program
        self.group_api_course.get_courses_in_group.return_value = self.courses
        result = assign_student_to_program(self.user, self.client, self.program_id)
        expected_message = (messages.ERROR,
                            'Unable to enroll you in the requested program, '
                            'Test program. No remaining places.')
        self.assertEqual(result.message, expected_message)


class TestIsFutureStart(TestCase):
    ''' Unit test for the method is_future_start from controller'''

    def setUp(self):
        self.current_time = datetime.datetime.now()

    def test_with_future_date(self):
        self.current_time += datetime.timedelta(2)
        self.assertTrue(is_future_start(self.current_time))

    def test_with_current_date(self):
        self.current_time -= datetime.timedelta(2)
        self.assertFalse(is_future_start(self.current_time))


class TestSendWarningEmailToAdmin(TestCase):
    ''' Unit test for the method send_warning_email_to_admin from controller'''

    def setUp(self):
        self.course_run = CourseRun(name='test', max_participants=5, course_id=1)

    def test_send_warning_email_to_admin(self):
        send_warning_email_to_admin(self.course_run)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, 'no-reply@mckinseyacademy.com')
        self.assertEqual(mail.outbox[0].to[0], 'no-reply@mckinseyacademy.com')
        self.assertEqual(mail.outbox[0].subject, 'Demo Registration - Warning')


@ddt.ddt
class TestSendEmail(TestCase):
    ''' Unit test for the method send_email from controller'''

    @ddt.data(
        ('subject-1', 'template_text-1', 'test1@test.com'),
        ('subject-2', 'template_text-2', 'test2@test.com'),
        ('subject-3', 'template_text-3', 'test3@test.com'),
        ('subject-4', 'template_text-4', 'test4@test.com')
    )
    def test_send_email(self, data):
        template = 'registration/public_registration_warning.haml'
        subject, template_text, email = data
        expected_body = 'Thisisasystemgeneratedwarningmessagetonotifyyouwehav' \
                        'ehitusersofthemaxlimitofusersonthecourse.'

        send_email(template, subject, '', template_text, 'test', email)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], email)
        self.assertEqual(mail.outbox[0].subject, subject)
        body = mail.outbox[0].body.replace(' ', '').replace('\n', '')
        self.assertEqual(body, expected_body)


class TestSendPasswordResetEmail(TestCase):
    ''' Unit test for the method send_password_reset_email from controller'''

    def setUp(self):
        self.domain = 'test_domain.com'
        self.user = DottableDict({'id': '1', 'username': 'test', 'email': 'test@test.com'})

    def test_send_password_reset_email(self):
        send_password_reset_email(self.domain, self.user, True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, 'no-reply@mckinseyacademy.com')
        self.assertEqual(mail.outbox[0].to[0], self.user.email)
        self.assertEqual(mail.outbox[0].subject, 'Password Reset Requested')


class TestUserActivationWithData(TestCase, ApplyPatchMixin):
    ''' Unit test for the method user_activation_with_data  from controller'''

    def setUp(self):
        self.user = DottableDict({'id': 1, 'username': 'test', 'email': 'test@test.com'})
        self.user_activation = UserActivation.user_activation(self.user)
        self.user_api = self.apply_patch('accounts.controller.user_api')

    def test_with_existing_user(self):
        self.user_api.update_user_information.return_value = HttpResponseBase(status=200)
        self.user_api.activate_user.return_value = HttpResponseBase(status=200)
        user_activation_with_data(self.user.id, self.user, self.user_activation)
        self.assertEqual(UserActivation.objects.count(), 0)

    def test_non_existing_user(self):
        self.user_api.update_user_information.side_effect = make_side_effect_raise_api_error(404)
        self.user_api.activate_user.return_value = HttpResponseBase(status=200)
        with self.assertRaises(ActivationError):
            user_activation_with_data(self.user.id, self.user, self.user_activation)

    def test_with_failed_activation(self):
        self.user_api.update_user_information.return_value = HttpResponseBase(status=200)
        self.user_api.activate_user.side_effect = make_side_effect_raise_api_error(404)
        with self.assertRaises(ActivationError):
            user_activation_with_data(self.user.id, self.user, self.user_activation)

    def test_user_with_no_activation_record(self):
        self.user_api.update_user_information.return_value = HttpResponseBase(status=200)
        self.user_api.activate_user.return_value = HttpResponseBase(status=200)
        self.user_activation.delete()

        user_activation_with_data(self.user.id, self.user, self.user_activation)
        self.assertEqual(UserActivation.objects.count(), 0)


class TestIoNewClientImage(TestCase):
    ''' Unit test for the method io_new_client_image from controller'''

    def setUp(self):
        from PIL import Image
        self.img = Image.new('RGB', (80, 128), (255, 255, 255))

    def test_io_new_client_image(self):
        self.img.save("images/old_image.jpg", 'JPEG')
        io_new_client_image('images/old_image.jpg', 'images/new_image.jpg')
        self.assertTrue(default_storage.exists('images/new_image.jpg'))
        self.assertFalse(default_storage.exists('images/old_image.jpg'))
        delete_files(['images/new_image.jpg'])

    def test_with_no_existing_image(self):
        with self.assertRaises(IOError):
            io_new_client_image('images/invalid_image.jpg', 'images/new_image.jpg')


class TestSaveNewClientImage(TestCase, ApplyPatchMixin):
    ''' Unit test for the method  save_new_client_image from controller'''

    def setUp(self):
        from PIL import Image
        self.img = Image.new('RGB', (80, 128), (255, 255, 255))
        self.organization_api = self.apply_patch('api_client.organization_models.organization_api')
        self.client = Client()
        setattr(self.client, 'id', 1)
        self.organization_api.update_organization.return_value = True

    def test_save_new_client_image(self):
        different_sizes = settings.COMPANY_GENERATE_IMAGE_SIZES
        self.img.save('images/old_image.jpg', 'JPEG')
        self.img.save('images/old_image-{}.jpg'.format(different_sizes[0][0]), 'JPEG')
        self.img.save('images/old_image-{}.jpg'.format(different_sizes[1][0]), 'JPEG')

        save_new_client_image('images/old_image.jpg', 'images/new_image.jpg', self.client)
        self.assertTrue(default_storage.exists('images/new_image.jpg'))
        self.assertTrue(default_storage.exists('images/new_image-{}.jpg'.format(different_sizes[0][0])))
        self.assertTrue(default_storage.exists('images/new_image-{}.jpg'.format(different_sizes[1][0])))
        self.assertFalse(default_storage.exists('images/old_image.jpg'))
        self.assertFalse(default_storage.exists('images/old_image-{}.jpg'.format(different_sizes[0][0])))
        self.assertFalse(default_storage.exists('images/old_image-{}.jpg'.format(different_sizes[1][0])))
        file_paths = [
            'images/new_image.jpg',
            'images/new_image-{}.jpg'.format(different_sizes[0][0]),
            'images/new_image-{}.jpg'.format(different_sizes[1][0])
        ]
        delete_files(file_paths)

    def test_with_no_existing_image(self):
        self.assertIsNone(save_new_client_image('images/invalid.jpg', 'images/new_image.jpg', self.client))


class TestGetMobileAppsId(TestCase, ApplyPatchMixin):
    ''' Unit test for the method get_mobile_apps_id from controller'''

    def setUp(self):
        self.get_mobile_apps = self.apply_patch('api_data_manager.organization_data.get_mobile_apps')
        self.organization = DottableDict({'id': 1})

    def test_with_mobile_apps(self):
        self.get_mobile_apps.return_value = DottableDict(
            {'results': [{'name': 'demo',
                          'deployment_mechanism': 1,
                          'ios_app_id': 1,
                          'android_app_id': 2}]
             })
        result = get_mobile_apps_id(self.organization.id)
        self.assertEqual(result['ios_app_id'], 1)
        self.assertEqual(result['android_app_id'], 2)
        self.assertEqual(result['user_org'], 'demo')

    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache', }})
    def test_without_mobile_apps(self):
        self.get_mobile_apps.side_effect = make_side_effect_raise_api_error(404)
        result = get_mobile_apps_id(self.organization.id)
        self.assertIsNone(result['ios_app_id'])
        self.assertIsNone(result['android_app_id'])
        self.assertIsNone(result['user_org'])

    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache', }})
    def test_with_invalid_deployment_mechanism(self):
        self.get_mobile_apps.return_value = DottableDict(
            {'results': [{'name': 'demo',
                          'deployment_mechanism': 2,
                          'ios_app_id': 1,
                          'android_app_id': 2}]
             })
        result = get_mobile_apps_id(self.organization.id)
        self.assertIsNone(result['ios_app_id'])
        self.assertIsNone(result['android_app_id'])
        self.assertIsNone(result['user_org'])


class TestGetSsoProvider(TestCase, ApplyPatchMixin):
    ''' Unit test for the method get_sso_provider from controller'''

    def setUp(self):
        self.third_party_auth_api = self.apply_patch('accounts.controller.third_party_auth_api')
        self.email = 'test@test.com'

    def test_with_associations(self):
        self.third_party_auth_api.get_providers_by_login_id.return_value = [
            DottableDict({'provider_id': 'oauth-123456789'})
        ]
        self.assertEqual(get_sso_provider(self.email), '123456789')

    def test_without_associations(self):
        self.third_party_auth_api.get_providers_by_login_id.return_value = []
        self.assertIsNone(get_sso_provider(self.email))


class TestSetNumberOfEnrolledUsers(TestCase, ApplyPatchMixin):
    ''' Unit test for the method _set_number_of_enrolled_users from controller'''
    def setUp(self):
        self.course_api = self.apply_patch('accounts.controller.course_api')
        self.course_run = CourseRun(course_id=1, total_participants=0)

    def test_with_users(self):
        self.course_api.get_user_list_json.return_value = json.dumps([{
            "id": 9,
            "email": "user@m.com",
            "username": "user",
            "first_name": "user",
            "last_name": "Tester"
        }, {
            "id": 7,
            "email": "user@m.com",
            "username": "user",
            "first_name": "user",
            "last_name": "Tester"
        }, {
            "id": 8,
            "email": "user@m.com",
            "username": "user",
            "first_name": "user",
            "last_name": "Tester"
        }])
        self.course_api.get_users_filtered_by_role.return_value = [DottableDict(
            {"role": "instructor", "id": 7}), DottableDict({"role": "instructor", "id": 9})]
        users = _set_number_of_enrolled_users(self.course_run)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['id'], 8)
        self.assertEqual(self.course_run.total_participants, 1)

    def test_non_existing_user(self):
        self.course_api.get_user_list_json.return_value = json.dumps([])
        self.course_api.get_users_filtered_by_role.return_value = []
        users = _set_number_of_enrolled_users(self.course_run)
        self.assertEqual(len(users), 0)
        self.assertEqual(self.course_run.total_participants, 0)
