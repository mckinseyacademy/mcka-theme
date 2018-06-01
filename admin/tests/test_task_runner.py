""" Tests for TaskRunner class"""

from ddt import ddt, data
from celery.decorators import task
from celery.states import ALL_STATES

from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from accounts.tests.utils import ApplyPatchMixin
from admin.bulk_task_runner import BulkTaskRunner
from util.unit_test_helpers.common_mocked_objects import TestUser

TEST_TASKS = (
    ('participants_csv_data', {'course_id': 'xyz', 'company_id': 'abc', 'base_url': 'http://abc.xyz'}),
    ('push_notifications_data', {'course_id': 'xyz', 'company_id': 'abc'}),
)


@task
def mocked_task(*args, **kwargs):
    """
    Replacement of real celery tasks for testing purpose
    """
    return {}


@ddt
class BulkTaskRunnerTests(TestCase, ApplyPatchMixin):
    """
    Test cases for BulkTaskRunner
    """
    def setUp(self):
        super(BulkTaskRunnerTests, self).setUp()

        self.request = RequestFactory().get('/')
        self.request.user = TestUser

        # Patching tasks as we'r testing task runner and not the actual tasks
        self.apply_patch('admin.bulk_task_runner.course_participants_data_retrieval_task', new=mocked_task)
        self.apply_patch('admin.bulk_task_runner.participants_notifications_data_task', new=mocked_task)

    def test_initialization(self):
        """
        Tests that task runner is initialized
        """
        task_name, params = TEST_TASKS[0]

        task_runner = BulkTaskRunner(
            request=self.request, params=params,
            task_name=task_name
        )

        self.assertIsInstance(task_runner, BulkTaskRunner)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @data(*TEST_TASKS)
    def test_task_execution(self, task):
        """
        Tests that TaskRunner is able to execute tasks
        """
        task_name, params = task

        task_runner = BulkTaskRunner(
            request=self.request, params=params,
            task_name=task_name
        )

        task_id = task_runner.execute_task()

        self.assertIsNotNone(task_id)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_get_task_result(self):
        """
        Tests getting a task result
        """
        task_name, params = TEST_TASKS[0]

        task_id = BulkTaskRunner(
            request=self.request, params=params,
            task_name=task_name
        ).execute_task()

        result = BulkTaskRunner.get_task_result(task_id=task_id)

        self.assertIsInstance(result, list)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_get_task_state(self):
        """
        Tests getting a task state
        """
        task_name, params = TEST_TASKS[0]

        task_id = BulkTaskRunner(
            request=self.request, params=params,
            task_name=task_name
        ).execute_task()

        state, info = BulkTaskRunner.get_task_state(task_id=task_id)

        self.assertIn(state, ALL_STATES)
