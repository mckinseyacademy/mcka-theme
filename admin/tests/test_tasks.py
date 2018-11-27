""" Tests for admin app celery tasks """
import ddt

from django.core import mail
from django.test import TestCase, override_settings

from util.unit_test_helpers import ApplyPatchMixin
from util.unit_test_helpers.common_mocked_objects import mock_storage_save
from admin.tasks import (
    course_participants_data_retrieval_task,
    send_export_stats_status_email,
    export_stats_status_email_task,
    participants_notifications_data_task,
    users_program_association_task
)
from api_client.course_models import CourseCohortSettings
from api_client.user_models import UserResponse


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
