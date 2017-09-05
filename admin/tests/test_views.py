import imp
from functools import wraps

from ddt import ddt, data

from django.test import TestCase, override_settings
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils.decorators import available_attrs
from rest_framework import status

from accounts.tests.tests import ApplyPatchMixin
from admin import views as admin_views
from .test_task_runner import mocked_task


def mocked_permission_group_required_api(*group_names):
    """
    Mocks permission group decorator
    """
    def decorator(view_fn):
        def _wrapped_view(self, request, *args, **kwargs):
            return view_fn(self, request, *args, **kwargs)
        return wraps(view_fn, assigned=available_attrs(view_fn))(_wrapped_view)
    return decorator


@override_settings(CELERY_ALWAYS_EAGER=True)
def mocked_execute_task(task_runner):
    """
    Mocks task runner execute method to run fake task
    """
    task_id = mocked_task.delay().task_id

    return task_id


@ddt
class TestBulkTaskAPI(TestCase, ApplyPatchMixin):
    """
    Tests bulk task API endpoints
    """
    def setUp(self):
        super(TestBulkTaskAPI, self).setUp()

        self.apply_patch(
            'admin.views.BulkTaskRunner.execute_task',
            new=mocked_execute_task
        )

        # patch the authentication decorator to bypass auth
        self.apply_patch(
            'lib.authorization.permission_group_required_api',
            new=mocked_permission_group_required_api
        )

        # reload module to apply mocked decorator
        imp.reload(admin_views)

        self.client = Client()
        self.api_url = reverse('bulk_task_api')

    def test_post_method(self):
        """
        Tests post method of API which creates a background task
        """
        response = self.client.post(path=self.api_url, data={
            'task_name': 'test_task'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data.get('task_id'))

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @data(
        ('PROGRESS', {'percentage': 50}),
        ('SUCCESS', {}),
    )
    def test_get_method(self, task_state):
        """
        Tests get method of API which returns a task status
        """
        task_id = mocked_task.delay().task_id

        state, result = task_state

        runner = self.apply_patch('admin.views.BulkTaskRunner')
        runner.get_task_state.return_value = state, result

        response = self.client.get(path=self.api_url, data={
            'task_id': task_id
        })

        response_data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test task progress is returned
        if state == 'PROGRESS':
            self.assertEqual(
                response_data.get('values', {}).get('progress'),
                result.get('percentage')
            )
        
        # test response for success case
        if state == 'SUCCESS':
            self.assertEqual(response_data.get('values', {}).get('progress'), '100')
