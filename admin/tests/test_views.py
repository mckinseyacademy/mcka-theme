import json
from functools import wraps

from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.utils.decorators import available_attrs
from mock import patch, Mock
from rest_framework import status

from accounts.models import RemoteUser
from accounts.tests.utils import ApplyPatchMixin, make_course, make_user
from admin.models import Client as ClientModel
from admin.views import client_sso, CourseDetailsApi
from api_client import user_api, group_api
from api_client.api_error import ApiError
from api_client.json_object import JsonParser
from lib.authorization import permission_groups_map
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


# TODO: mock API to fix test and uncomment
# class AdminViewTest(TestCase, ApplyPatchMixin):
#     """ Tests related to admin.views """
#     def setUp(self):
#         """ Setup admin views test """
#         super(AdminViewTest, self).setUp()
#         self.client = Client()
#         self.user = DottableDict({
#             "id": '1',
#             "username": 'mcka_admin_test_user',
#             "first_name": 'mcka_admin',
#             "last_name": 'Tester',
#             "email": "mcka_admin_test_user@mckinseyacademy.com",
#             "password": "PassworD12!@",
#             'is_mcka_admin': True
#         })
#         self.url_name = 'edit_client_mobile_image'
#         self.parameters = {
#             'client_id': 1,
#         }
#         mobile_api = self.apply_patch('api_client.mobileapp_api')
#         mobile_api.get_mobile_app_themes.return_value = []
#
#     def test_edit_client_mobile_image_logo(self):
#         """ test edit mobile logo page """
#
#         self.parameters['img_type'] = 'logo'
#         edit_client_mobile_image_url_logo = reverse(self.url_name, kwargs=self.parameters)
#         respose = self.client.get(edit_client_mobile_image_url_logo)
#         self.assertEqual(respose.status_code, status.HTTP_200_OK)
#
#     def test_edit_client_mobile_image_header(self):
#         """ test edit mobile header page """
#
#         self.parameters['img_type'] = 'header'
#         edit_client_mobile_image_url_header = reverse(self.url_name, kwargs=self.parameters)
#         respose = self.client.get(edit_client_mobile_image_url_header)
#         self.assertEqual(respose.status_code, status.HTTP_200_OK)
#
#     def test_edit_client_mobile_image_invalid(self):
#         """ test edit mobile logo/header page for invalid request """
#
#         self.parameters['img_type'] = 'invalid'
#         edit_client_mobile_image_url_invalid = reverse(self.url_name, kwargs=self.parameters)
#         respose = self.client.get(edit_client_mobile_image_url_invalid)
#         self.assertEqual(respose.status_code, status.HTTP_404_NOT_FOUND)


# TODO: mock API to fix test and uncomment
# @ddt
# class TestBulkTaskAPI(TestCase, ApplyPatchMixin):
#     """
#     Tests bulk task API endpoints
#     """
#
#     def setUp(self):
#         super(TestBulkTaskAPI, self).setUp()
#
#         self.apply_patch(
#             'admin.views.BulkTaskRunner.execute_task',
#             new=mocked_execute_task
#         )
#         _create_user()
#         self.client = Client()
#         self.client.login(username='mcka_admin_test_user', password='PassworD12!@')
#         self.api_url = reverse('bulk_task_api')
#
#     def test_post_method(self):
#         """
#         Tests post method of API which creates a background task
#         """
#         response = self.client.post(path=self.api_url, data={
#             'task_name': 'test_task'
#         })
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertIsNotNone(response.data.get('task_id'))
#
#     @override_settings(CELERY_ALWAYS_EAGER=True)
#     @data(
#         ('PROGRESS', {'percentage': 50}),
#         ('SUCCESS', {}),
#     )
#     def test_get_method(self, task_state):
#         """
#         Tests get method of API which returns a task status
#         """
#         task_id = mocked_task.delay().task_id
#
#         state, result = task_state
#
#         runner = self.apply_patch('admin.views.BulkTaskRunner')
#         runner.get_task_state.return_value = state, result
#
#         response = self.client.get(path=self.api_url, data={
#             'task_id': task_id
#         })
#
#         response_data = response.data
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         # test task progress is returned
#         if state == 'PROGRESS':
#             self.assertEqual(
#                 response_data.get('values', {}).get('progress'),
#                 result.get('percentage')
#             )
#
#         # test response for success case
#         if state == 'SUCCESS':
#             self.assertEqual(response_data.get('values', {}).get('progress'), '100')


class AdminClientSSOTest(TestCase, ApplyPatchMixin):

    def setUp(self):
        user_api = self.apply_patch('accounts.controller.user_api')
        is_user_in_permission_group_lib = self.apply_patch("lib.authorization.is_user_in_permission_group")
        is_user_in_permission_group_lib.return_value = True
        is_user_in_permission_group_accounts = self.apply_patch("accounts.models.is_user_in_permission_group")
        is_user_in_permission_group_accounts.return_value = True
        fetch_programs = self.apply_patch('admin.views.Client.fetch_programs')
        fetch_programs.return_value = []

        self.factory = RequestFactory()
        self.user = RemoteUser.objects.create_user(
            username='johndoe', email='john@doe.org', password='password')
        self.mock_session = Mock(session_key='', __contains__=lambda _a, _b: False)

        org_data_str = json.dumps({
            "url": "http://lms.mcka.local/api/server/organizations/1/",
            "id": 1,
            "name": "test_company",
            "display_name": "Test Company Inc",
            "contact_name": "Test Company",
            "contact_email": "contact@test.company",
            "contact_phone": "112233445566",
            "logo_url": "",
            "created": "2018-03-05T15:20:51.096508Z",
            "modified": "2018-04-26T13:02:53.077131Z"
        })
        mock_fetch_organization = self.apply_patch('api_client.organization_api.fetch_organization')
        mock_fetch_organization.return_value = JsonParser.from_json(org_data_str, ClientModel)

    def test_no_access_keys_message(self):
        request = self.factory.get('/admin/clients/1/sso')
        request.user = self.user
        request.session = self.mock_session
        response = client_sso(request, 1)
        self.assertIn('No access keys', response.content)

    def test_save_identity_provider_success(self):
        test_provider = 'test-provider'
        request = self.factory.post('/admin/clients/1/sso', {
            'identity_provider': test_provider,
        })
        request.user = self.user
        request.session = self.mock_session
        response = client_sso(request, 1)
        idp_input_html = """
            <input id='identity_provider' type='text' name='identity_provider' value='{}' />
        """.format(test_provider)
        self.assertInHTML(idp_input_html, response.content)


class CourseParticipantsStatsMixin(ApplyPatchMixin):
    """
    Utilities for testing the views that use CourseParticipantsStats.
    """
    def setUp(self):
        """
        Create the base data.
        """
        super(CourseParticipantsStatsMixin, self).setUp()
        self.course = make_course(course_id='course_1', display_name='Course One')
        self.students = [
            make_user(username="student{}".format(idx), email="student{}@example.com".format(idx))
                for idx in range(4)
        ]
        self.admin_user = make_user(username="mcka_admin", email="mcka_admin@example.com")
        self.admin_user.is_internal_admin = True
        self.admin_user.is_company_admin = False
        self.factory = RequestFactory()

    def get_request(self, url, user=None):
        """
        GET the given URL, for the optional user, and return the request.
        """
        request = self.factory.get(url)
        if user:
            request.user = user
            request.session = Mock(session_key='', __contains__=lambda _a, _b: False)
        return request

    def patch_user_permissions(self):
        """
        Patch the authorization hit to say that the mcka_admin is in all groups.
        """
        def admin_is_in_all_groups(user, *_args, **_kwargs):
            """
            Our admin user is in all groups.
            """
            return (user.username == self.admin_user.username)

        lib_auth = self.apply_patch("lib.authorization.is_user_in_permission_group")
        lib_auth.side_effect = admin_is_in_all_groups

    def patch_course_users(self, students):
        """
        Patch the given api method with course user data.
        """
        api_data = {
            'results': [
                {
                    'id': student.id,
                    'username': student.username,
                    'email': student.email,
                    'is_active': True,
                } for student in students
            ],
            'next': ''
        }
        api_data['count'] = len(api_data['results'])
        api_client = self.apply_patch('admin.controller.course_api')
        api_client.get_course_details_users.return_value = api_data
        # When coerced to an int, a mock returns 1, which messes up completions, so
        # instead return no completions at all to get the desired result.
        api_client.get_course_completions.return_value = {}
        return api_client

    def assert_expected_result(self, result, idx=0):
        """
        Ensure that the expected data was returned.
        """
        expected_data = {
            'is_active': True,
            'id': None,  # for some reason, these demo users don't have IDs
            'email': self.students[idx].email,
            'username': self.students[idx].username,
            'activation_link': "",
            'custom_user_status': 'Participant',
            'custom_activated': 'Yes',
            'custom_last_login': '-',
            'assessments': [],
            'groupworks': [],
            'number_of_groupworks': 0,
            'organizations': [{'display_name': 'No company'}],
            'organizations_display_name': 'No company',
            'engagement': 0,
            'proficiency': '000',
            'progress': '000',
            'number_of_assessments': 0,
        }
        self.assertEqual(expected_data, result)


class CourseDetailsApiTest(CourseParticipantsStatsMixin, TestCase):
    """
    Test the CourseDetailsApi view.
    """
    def setUp(self):
        """
        Patch the required APIs
        """
        super(CourseDetailsApiTest, self).setUp()
        self.patch_course_users(self.students)
        self.patch_user_permissions()
        self.maxDiff = None

    def test_get(self):
        """
        Test GET /admin/api/courses/<course_id>
        """
        course_detail_url = reverse('course_details_api', kwargs={'course_id': unicode(self.course.course_id)})
        request = self.get_request(course_detail_url, self.admin_user)
        response = CourseDetailsApi().get(request, self.course.course_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)
        for idx in range(4):
            self.assert_expected_result(response.data["results"][idx], idx)
