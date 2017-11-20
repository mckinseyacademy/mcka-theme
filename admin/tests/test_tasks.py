""" Tests for admin app celery tasks """
import unicodecsv as csv

from django.test import TestCase, override_settings

from accounts.tests.utils import ApplyPatchMixin
from admin.tasks import (
    course_participants_data_retrieval_task,
    participants_notifications_data_task,
    users_program_association_task
)


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
            'lesson_completions': {'lesson_number': 5, 'completion': 90}
        },
        {
            'id': 'user_2',
            'groupworks': [{'label': 'xyz', 'percent': '98'}],
            'assessments': [{'label': 'xyz', 'percent': '95'}],
            'lesson_completions': {'lesson_number': 5, 'completion': 90}
        },
        {
            'id': 'user_3',
            'groupworks': [{'label': 'xyz', 'percent': '98'}],
            'assessments': [{'label': 'xyz', 'percent': '95'}],
            'lesson_completions': {'lesson_number': 5, 'completion': 90}
        },
        {
            'id': 'user_4',
            'groupworks': [{'label': 'xyz', 'percent': '98'}],
            'assessments': [{'label': 'xyz', 'percent': '95'}],
            'lesson_completions': {'lesson_number': 5, 'completion': 90}
        },
        {
            'id': 'user_5',
            'groupworks': [{'label': 'xyz', 'percent': '98'}],
            'assessments': [{'label': 'xyz', 'percent': '95'}],
            'lesson_completions': {'lesson_number': 5, 'completion': 90}
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


class BulkTasksTest(TestCase, ApplyPatchMixin):
    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_course_participants_data_retrieval_task(self):
        """
        Tests participants data retrieval task
        """
        self.apply_patch('admin.tasks.CourseParticipantStats', new=MockParticipantsStats)

        test_course_id = 'abc'
        file_name = '{}_user_stats'.format(test_course_id)

        result = course_participants_data_retrieval_task(
            course_id=test_course_id, company_id=None, base_url='http://url.xyz',
            task_id='xyz'
        )

        self.assertIn(file_name, result)

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
        group_api.add_user_to_group.return_value = True

        user_ids = [1, 2, 3]

        result = users_program_association_task(
            program_id='abc', user_ids=user_ids, task_id='xyz'
        )

        self.assertEqual(result.get('total'), len(user_ids))
