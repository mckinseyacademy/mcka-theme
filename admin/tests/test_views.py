from functools import wraps

from ddt import ddt, data
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.test.client import Client
from django.utils.decorators import available_attrs
from mock import patch
from rest_framework import status

from api_client.group_api import PERMISSION_GROUPS
from lib.authorization import permission_groups_map, permission_group_required
from accounts.tests.utils import ApplyPatchMixin
from api_client import user_api, group_api
from api_client.api_error import ApiError
from lib.utils import DottableDict
from .test_task_runner import mocked_task


_FAKE_USER_OBJ = DottableDict({
    "id": '1',
    "username": 'mcka_admin_test_user',
    "first_name": 'mcka_admin',
    "last_name": 'Tester',
    "email": "mcka_admin_test_user@mckinseyacademy.com",
    "password": "PassworD12!@",
    'is_mcka_admin': True
})


def _fake_permission_group_required(*group_names):  # pylint: disable=unused-argument
    """
    Fake method for permission_group_required method
    """

    def decorator(view_fn):
        def _wrapped_view(request, *args, **kwargs):
            # faking request user
            request.user = _FAKE_USER_OBJ
            return view_fn(request, *args, **kwargs)

        return wraps(view_fn, assigned=available_attrs(view_fn))(_wrapped_view)

    return decorator


permission_patcher = patch(
    'lib.authorization.permission_group_required',
    _fake_permission_group_required
).start()



def _create_user():
    """
    create a test user
    """
    user_data = {
        "username": 'mcka_admin_test_user',
        "first_name": 'mcka_admin',
        "last_name": 'Tester',
        "email": "mcka_admin_test_user@mckinseyacademy.com",
        "password": "PassworD12!@"
    }
    users = user_api.get_users(username=user_data['username'])
    if users:
        return users[0]

    try:
        user = user_api.register_user(user_data)
        if user:
            group_api.add_user_to_group(
                user.id,
                permission_groups_map()[group_api.PERMISSION_GROUPS.MCKA_ADMIN]
            )
            return user
    except ApiError:
        pass


@override_settings(CELERY_ALWAYS_EAGER=True)
def mocked_execute_task(task_runner):
    """
    Mocks task runner execute method to run fake task
    """
    task_id = mocked_task.delay().task_id

    return task_id


class AdminViewTest(TestCase, ApplyPatchMixin):
    """ Tests related to admin.views """
    def setUp(self):
        """ Setup admin views test """
        super(AdminViewTest, self).setUp()
        self.client = Client()
        self.user = DottableDict({
            "id": '1',
            "username": 'mcka_admin_test_user',
            "first_name": 'mcka_admin',
            "last_name": 'Tester',
            "email": "mcka_admin_test_user@mckinseyacademy.com",
            "password": "PassworD12!@",
            'is_mcka_admin': True
        })
        self.url_name = 'edit_client_mobile_image'
        self.parameters = {
            'client_id': 1,
        }
        mobile_api = self.apply_patch('api_client.mobileapp_api')
        mobile_api.get_mobile_app_themes.return_value = []


    def test_edit_client_mobile_image_logo(self):
        """ test edit mobile logo page """

        self.parameters['img_type'] = 'logo'
        edit_client_mobile_image_url_logo = reverse(self.url_name, kwargs=self.parameters)
        respose = self.client.get(edit_client_mobile_image_url_logo)
        self.assertEqual(respose.status_code, status.HTTP_200_OK)

    def test_edit_client_mobile_image_header(self):
        """ test edit mobile header page """

        self.parameters['img_type'] = 'header'
        edit_client_mobile_image_url_header = reverse(self.url_name, kwargs=self.parameters)
        respose = self.client.get(edit_client_mobile_image_url_header)
        self.assertEqual(respose.status_code, status.HTTP_200_OK)

    def test_edit_client_mobile_image_invalid(self):
        """ test edit mobile logo/header page for invalid request """

        self.parameters['img_type'] = 'invalid'
        edit_client_mobile_image_url_invalid = reverse(self.url_name, kwargs=self.parameters)
        respose = self.client.get(edit_client_mobile_image_url_invalid)
        self.assertEqual(respose.status_code, status.HTTP_404_NOT_FOUND)


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
        _create_user()
        self.client = Client()
        self.client.login(username='mcka_admin_test_user', password='PassworD12!@')
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

