""" Tests for admin app celery tasks """
import ddt
from mock import patch, Mock

from django.core import mail
from django.test import TestCase, override_settings

from admin.models import AccessKey, ClientNavLinks, ClientCustomization, BrandingSettings, LearnerDashboard, \
    CompanyInvoicingDetails, CompanyContact, DashboardAdminQuickFilter
from admin.tasks import (
    course_participants_data_retrieval_task,
    send_export_stats_status_email,
    export_stats_status_email_task,
    participants_notifications_data_task,
    users_program_association_task,
    create_problem_response_report,
    monitor_problem_response_report,
    post_process_problem_response_report,
    delete_participants_task,
    delete_company_task,
)
from admin.tests.test_views import CourseParticipantsStatsMixin
from admin.tests.utils import Dummy
from api_client.course_models import CourseCohortSettings
from api_client.user_models import UserResponse
from celery.exceptions import Retry
from public_api.models import ApiToken
from util.unit_test_helpers import ApplyPatchMixin, make_side_effect_raise_api_error
from util.unit_test_helpers.common_mocked_objects import mock_storage_save


class MockParticipantsStats(object):
    """
    Mocks the participants data retrieval utility
    """
    count = 0
    participant_data = [
        {
            'id': 'user_1',
            'groupworks': [{'label': 'xyz', 'percent': '98'}],
            'assessments': [{'label': 'xyz', 'percent': '95'}],
            'lesson_completions': {'lesson_number': 5, 'completion': 90},
            'attributes': []
        },
        {
            'id': 'user_2',
            'groupworks': [{'label': 'xyz', 'percent': '98'}],
            'assessments': [{'label': 'xyz', 'percent': '95'}],
            'lesson_completions': {'lesson_number': 5, 'completion': 90},
            'attributes': []
        },
        {
            'id': 'user_3',
            'groupworks': [{'label': 'xyz', 'percent': '98'}],
            'assessments': [{'label': 'xyz', 'percent': '95'}],
            'lesson_completions': {'lesson_number': 5, 'completion': 90},
            'attributes': []
        },
        {
            'id': 'user_4',
            'groupworks': [{'label': 'xyz', 'percent': '98'}],
            'assessments': [{'label': 'xyz', 'percent': '95'}],
            'lesson_completions': {'lesson_number': 5, 'completion': 90},
            'attributes': []
        },
        {
            'id': 'user_5',
            'groupworks': [{'label': 'xyz', 'percent': '98'}],
            'assessments': [{'label': 'xyz', 'percent': '95'}],
            'lesson_completions': {'lesson_number': 5, 'completion': 90},
            'attributes': []
        },

    ]

    def __init__(self, *args, **kwargs):
        pass

    def participant_record_parser(self, *args, **kwargs):
        pass

    def get_participants_data(self, api_params):
        if self.count == 4:
            next_url = None
        else:
            next_url = 'http://next.url'

        data = self.participant_data[self.count]
        self.count += 1

        return {
            'results': [data],
            'count': 5,
            'next': next_url
        }


@ddt.ddt
class BulkTasksTest(TestCase, ApplyPatchMixin):
    def setUp(self):
        super(BulkTasksTest, self).setUp()

        # mocking storage save to prevent creating actual files
        self.apply_patch(
            'django.core.files.storage.FileSystemStorage.save',
            new=mock_storage_save
        )

        user_api = self.apply_patch('admin.tasks.user_api')
        user_api.get_user.return_value = UserResponse(dictionary={
            "id": 1, 'username': 'user1', 'email': 'user@exmple.com', 'first_name': 'Test User', 'is_active': True
        })

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_course_participants_data_retrieval_task(self):
        """
        Tests participants data retrieval task
        """
        self.apply_patch('admin.tasks.CourseParticipantStats', new=MockParticipantsStats)

        test_course_id = 'abc'
        file_name = '{}_user_stats'.format(test_course_id)

        course_api = self.apply_patch('admin.tasks.course_api')
        course_api.get_cohorts_settings.return_value = CourseCohortSettings(
            dictionary={'is_cohorted': True, 'id': 1}
        )
        result = course_participants_data_retrieval_task(
            course_id=test_course_id, company_id=None, base_url='http://url.xyz',
            task_id='xyz', user_id=123
        )

        self.assertIn(file_name, result)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_export_stats_notification_email_task(self):
        """
        Tests export stats email notification task
        """
        export_stats_status_email_task(
            user_id=123, course_id='xyz', report_name='test_report',
            base_url='http://abc.xyz', download_url='http://url.xyz',
            subject='subject', template='admin/export_stats_email_template.haml',
        )

        self.assertEqual(len(mail.outbox), 1)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @ddt.data(
        ('xyz', True,),
        ('abc', False,),
    )
    @ddt.unpack
    def test_send_notification_email(self, course_id, report_succeeded):
        """
        Tests send notification helper method
        """
        send_export_stats_status_email(
            user_id=123, course_id=course_id, report_name='test_report',
            base_url='http://abc.xyz', download_url='http://url.xyz',
            report_succeeded=report_succeeded,
        )

        if report_succeeded:
            subject = 'Participant stats for {} is ready to download'.format(course_id)
        else:
            subject = 'Participant stats for {} did not generate'.format(course_id)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, subject)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_participants_notifications_data_task(self):
        """
        Tests notifications data retrieval task
        """
        api_result = [{'id': 'user_1'}]
        course_api = self.apply_patch('admin.tasks.course_api')
        course_api.get_course_details_users.return_value = {
            'results': api_result,
            'count': 1,
            'next': ''
        }

        result = participants_notifications_data_task(
            course_id='abc', company_id=None, task_id='xyz'
        )

        self.assertEqual(result, api_result)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_users_program_association_task(self):
        """
        Tests users and program association task
        """
        group_api = self.apply_patch('admin.tasks.group_api')
        group_api.add_users_to_group.return_value = True

        user_ids = [1, 2, 3]

        result = users_program_association_task(
            program_id='abc', user_ids=user_ids, task_id='xyz'
        )

        self.assertEqual(result.get('total'), len(user_ids))


@ddt.ddt
class ProblemResponseTasksTest(TestCase):
    """Tests for tasks pertaining to problem response post-processing."""

    @patch(
        'admin.tasks.create_problem_response_report.request.id',
        return_value='task_id'
    )
    @patch(
        'admin.tasks.instructor_api.generate_problem_responses_report',
        return_value=Mock()
    )
    def test_create_problem_response_report(
        self, mock_generate_problem_responses_report, mock_task_id
    ):
        """Test create problem response report task."""
        create_problem_response_report.apply(args=('course_id', 'problem_location'))
        mock_generate_problem_responses_report.assert_called_with('course_id', 'problem_location', None)

    @ddt.data(
        {'task_id': 'remote_task_id', 'task_state': 'SUCCESS',
         'in_progress': False, 'task_progress': {'report_name': 'report_name'}},
        {'task_id': 'remote_task_id', 'task_state': 'PROGRESS',
         'in_progress': True, 'task_progress': {'report_name': 'report_name'}},
    )
    @patch('admin.tasks.instructor_api.get_task_status')
    @patch(
        'admin.tasks.monitor_problem_response_report.update_state',
        return_value=Mock()
    )
    @patch(
        'admin.tasks.monitor_problem_response_report.retry',
        return_value=Retry()
    )
    def test_monitor_problem_response_report(self, tasks_result, mock_retry, mock_update_state, mock_get_task_status):
        """Test monitor problem response report task."""
        mock_get_task_status.return_value = tasks_result
        if tasks_result['task_state'] == 'SUCCESS':
            monitor_problem_response_report(
                {'id': 'task_id', 'remote_task_id': 'remote_task_id'},
                'course_id'
            )
            self.assertEqual(len(mock_update_state.mock_calls), 1)
        else:
            with self.assertRaises(Retry):
                monitor_problem_response_report(
                    {'id': 'task_id', 'remote_task_id': 'remote_task_id'},
                    'course_id'
                )
        mock_get_task_status.assert_called_with('remote_task_id')

    @patch('admin.tasks.AdminTask.objects.get', return_value=Mock())
    @patch('admin.tasks.create_and_store_csv_file', return_value='file_url')
    @patch('admin.tasks.ProblemReportPostProcessor')
    @patch(
        'admin.tasks.instructor_api.get_report_downloads',
        return_value=[{'url': 'url', 'name': 'name'}]
    )
    def test_process_problem_response_report(
        self,
        mock_get_report_downloads,
        mock_processor,
        mock_store_file,
        mock_admin_task_get
    ):
        """Test process problem response report."""
        mock_processor().post_process.return_value = [{'key1': 'val1', 'key2': 'val2'}], ['key1', 'key2']
        mock_processor().module_lesson_number.return_value = ('module number', 'lesson number')
        post_process_problem_response_report(
            {'id': 'task_id', 'report_name': 'report_name'},
            'course_id',
            'problem_location'
        )
        mock_get_report_downloads.assert_called_with('course_id', 'report_name')
        mock_processor.assert_called_with(course_id='course_id', report_name='name', report_uri='url')
        self.assertEqual(len(mock_processor().post_process.mock_calls), 1)
        self.assertEqual(len(mock_store_file.mock_calls), 1)
        self.assertEqual(len(mock_admin_task_get().save.mock_calls), 1)


class DeleteParticipantsTaskTest(CourseParticipantsStatsMixin, TestCase):
    """Tests tasks required for bulk user deletion."""

    @patch('admin.tasks.get_path', lambda x: x)
    @patch('admin.tasks.get_users')
    @patch('admin.tasks.get_emails_from_csv')
    @patch('admin.controller.delete_participants')
    def test_delete_participants_task_with_file(
            self, delete_participants_mock, get_emails_from_csv_mock, get_users_mock
    ):
        """Test bulk user deletion task with users provided in CSV file."""
        stub_file = 'stub_file'
        emails = [user.email for user in self.students]
        get_users_mock.side_effect = lambda **kwargs: self.students
        get_emails_from_csv_mock.side_effect = lambda _: ('email', emails)

        delete_participants_task(stub_file, False, None, None)
        get_emails_from_csv_mock.assert_called_with(stub_file)
        get_users_mock.assert_called_with(**{'email': emails})
        delete_participants_mock.assert_called_with(None, users=self.students)

    @patch('admin.controller.delete_participants')
    def test_delete_participants_task_with_ids(self, delete_participants_mock):
        """Test bulk user deletion task with users' IDs provided directly."""
        student_ids = [student.id for student in self.students]

        delete_participants_task(student_ids, False, None, None)
        delete_participants_mock.assert_called_with(student_ids)


class DeleteCompanyTaskTest(CourseParticipantsStatsMixin, TestCase):
    """Tests tasks required for company deletion."""

    def setUp(self):
        super(DeleteCompanyTaskTest, self).setUp()
        self.mock_id = 0
        self.dummy_organization = Dummy()
        self.dummy_organization.display_name = 'dummy'

    @patch('admin.tasks.send_email')
    def test_delete_company_task_nonexistent_company(self, mock_send_email):
        """
        Test deleting company that doesn't exist in LMS.
        """
        mock_send_email.delay = Mock()
        delete_company_task(self.mock_id, {}, None)
        args, _ = mock_send_email.delay.call_args
        self.assertEqual('Company deletion completed', args[0])

    @patch('api_client.organization_api.delete_organization')
    @patch('admin.controller.remove_mobile_app_theme', side_effect=make_side_effect_raise_api_error(404))
    @patch('admin.tasks.delete_participants_task')
    @patch('api_client.organization_api.fetch_organization_user_ids')
    @patch('api_client.organization_api.fetch_organization')
    @patch('admin.controller.get_mobile_app_themes')
    def test_delete_company_race_condition(self, get_theme_mock, fetch_organization_mock, fetch_users_mock, *mocks):
        """
        Test deleting company with the race condition during removing mobile app theme.
        """
        get_theme_mock.return_value = [{'id': self.mock_id}]
        fetch_users_mock.return_value = [self.mock_id]
        fetch_organization_mock.return_value = self.dummy_organization

        delete_company_task(self.mock_id, {}, None)

        for mock in mocks:
            self.assertEqual(mock.call_count, 1)

    @patch('admin.controller.remove_mobile_app_theme')
    @patch('api_client.organization_api.delete_organization')
    @patch('admin.tasks.delete_participants_task')
    @patch('api_client.organization_api.fetch_organization_user_ids')
    @patch('api_client.organization_api.fetch_organization')
    @patch('admin.controller.get_mobile_app_themes')
    def test_delete_company(self, get_theme_mock, fetch_organization_mock, fetch_users_mock, *mocks):
        """
        Test deleting company as admin.
        """
        get_theme_mock.return_value = [{'id': self.mock_id}]
        fetch_users_mock.return_value = [self.mock_id]
        fetch_organization_mock.return_value = self.dummy_organization

        delete_company_task(self.mock_id, {}, None)
        for mock in mocks:
            self.assertEqual(mock.call_count, 1)

        client_models = (
            AccessKey,
            ClientNavLinks,
            ClientCustomization,
            BrandingSettings,
            LearnerDashboard,
            ApiToken,
        )
        for model in client_models:
            self.assertFalse(model.objects.filter(client_id=self.mock_id))

        company_models = (
            CompanyInvoicingDetails,
            CompanyContact,
            DashboardAdminQuickFilter,
        )
        for model in company_models:
            self.assertFalse(model.objects.filter(company_id=self.mock_id))
