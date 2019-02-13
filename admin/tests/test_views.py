import json
import ddt

from mcka_apros.celery import app as test_app

from django.contrib.sessions.middleware import SessionMiddleware
from django.core.files.uploadedfile import File
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseForbidden
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from mock import patch, Mock
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from waffle.testutils import override_switch

from accounts.models import RemoteUser
from accounts.tests.utils import ApplyPatchMixin, make_company, make_course, make_user, make_side_effect_raise_api_error
from admin import views
from admin.models import (
    Client as ClientModel,
    ClientCustomization,
    AdminTask,
)
from admin.tests.utils import get_deletion_waffle_switch, MockUser
from admin.views import client_sso, CourseDetailsApi
from api_client import user_api, group_api
from api_client.api_error import ApiError
from api_client.json_object import JsonParser
from lib.authorization import permission_groups_map
from .test_task_runner import mocked_task
from util.unit_test_helpers import AprosTestingClient
from api_client.group_api import PERMISSION_GROUPS
from api_data_manager.tests.utils import APIDataManagerMockMixin


def mock_task():
    @test_app.task(bind=True)
    def test_task(self, *args, **kwargs):
        """Test task."""
        pass
    return test_task


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
            group_api.add_users_to_group(
                [user.id],
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


class AdminViewTest(TestCase, ApplyPatchMixin, APIDataManagerMockMixin):
    """ Tests related to admin.views """
    client_class = AprosTestingClient

    def setUp(self):
        """ Setup admin views test """
        super(AdminViewTest, self).setUp()
        self.url_name = 'edit_client_mobile_image'
        self.parameters = {
            'client_id': 1,
        }
        mobile_api = self.apply_patch('admin.views.mobileapp_api')
        mobile_api.get_mobile_app_themes.return_value = []

        self.mock_user_api_data_manager(
            module_paths=[
                'accounts.middleware.thread_local.UserDataManager',
            ],
            data={'courses': [], 'current_course': None}
        )

        # Mock checking if user exists in middleware
        self.mock_get_user_dict = self.apply_patch('accounts.middleware.session_timeout.get_user_dict')

        # login as an uber admin
        self.client.login(user_role=PERMISSION_GROUPS.MCKA_ADMIN)

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


@ddt.ddt
class TestBulkTaskAPI(TestCase, ApplyPatchMixin):
    """
    Tests bulk task API endpoints
    """
    client_class = AprosTestingClient

    def setUp(self):
        super(TestBulkTaskAPI, self).setUp()

        self.apply_patch(
            'admin.views.BulkTaskRunner.execute_task',
            new=mocked_execute_task
        )
        self.client.login(user_role=PERMISSION_GROUPS.MCKA_ADMIN)
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
    @ddt.data(
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


class AdminClientSSOTest(TestCase, ApplyPatchMixin):

    def setUp(self):
        self.apply_patch('accounts.controller.user_api')
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
        self.students = [make_user(id=idx,
                                   username="student{}".format(idx),
                                   email="student{}@example.com".format(idx)) for idx in range(4)]
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

    def post_request(self, url,  user=None):
        """
        POST the given URL, for the optional user, and return the request.
        """
        self.patch_user_permissions()
        request = self.factory.post(url)
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

    def patch_course_users(self, students, users=None):
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
        # Note: if you pass an empty list of users, this will return all users.  This
        # matches the behavior of the real API, so apros has to work around this case
        # by not making the api call if no users are requested.
        if users:
            api_data['results'] = [student for student in api_data['results'] if student['id'] in users]
        api_data['count'] = len(api_data['results'])
        api_client = self.apply_patch('admin.controller.course_api')
        api_client.get_course_details_users.return_value = api_data
        # When coerced to an int, a mock returns 1, which messes up completions, so
        # instead return no completions at all to get the desired result.
        api_client.get_course_completions.return_value = {}
        api_client.get_course_social_metrics.return_value = {
            student.id: 0
            for student in self.students
        }
        return api_client

    def assert_expected_result(self, result, idx=0):
        """
        Ensure that the expected data was returned.
        """
        expected_data = {
            'is_active': True,
            'id': idx,
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


@ddt.ddt
class CourseDetailsTest(CourseParticipantsStatsMixin, TestCase):
    """
    Test course details view
    """

    def setUp(self):
        """
        Patch the required APIs
        """
        super(CourseDetailsTest, self).setUp()
        self.patch_course_users(self.students)
        self.patch_user_permissions()

    @ddt.unpack
    @ddt.data(
        (True, True, False, True),
        (False, False, False, False),
        (True, True, False, True),
        (False, True, False, True),
        (True, False, True, False),
        (False, False, True, False),
        (True, True, True, False),
        (False, True, True, False),
    )
    @patch('accounts.models.RemoteUser.is_client_admin', lambda x: False)
    def test_cohorts_groupwork(self, is_cohorted, is_available, is_client_admin, show_tab):
        """
        Make sure the cohort tab is correctly hidden or shown depending on
        groupwork and company admin or internal admin. Also makes sure the
        correct javascript variables are set for the client side.
        """
        def _get_course_context(t, org_id=''):
            return {
                'cohorts_enabled': t[0],
                'cohorts_available': t[1],
            }
        course_api = self.apply_patch('admin.views.load_course')
        course_api.return_value = (is_cohorted, is_available)

        url = reverse('course_details', kwargs={'course_id': unicode(self.course.course_id)})
        request = self.get_request(url, self.admin_user)
        request.url_name = 'course_details'
        with patch('admin.views.organization_api.fetch_organization', Mock()):
            with patch('admin.views._get_course_context', _get_course_context):
                if is_client_admin:
                    response = views.company_course_details(request, self.course.course_id, 1)
                else:
                    response = views.course_details(request, self.course.course_id)
                # Make sure the view works
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                # Make sure cohorts button is correctly shown/hidden
                self.assertEqual(show_tab, '/admin/cohorts/' in response.content)
                # Make sure javascript variables are correctly set
                self.assertTrue('var course_details_cohorts_enabled = \'%s\'' % is_cohorted in response.content)
                self.assertTrue('var course_details_cohorts_available = \'%s\'' % (
                        is_available and not is_client_admin) in response.content)


@ddt.ddt
class AdminCsvUploadViewsTest(CourseParticipantsStatsMixin, TestCase):
    """
    Test the enroll_participants_from_csv and import_participants views.
    """
    def setUp(self):
        super(AdminCsvUploadViewsTest, self).setUp()

    @ddt.unpack
    @ddt.data(
        (views.enroll_participants_from_csv, 'student_enroll_list',
         "admin/test_data/enroll-existing-participants.csv", True),
        (views.import_participants, 'student_list',
         "admin/test_data/enroll-existing-participants.csv", True),

        (views.enroll_participants_from_csv, '',
         "admin/test_data/enroll-existing-participants.csv", False),
        (views.import_participants, '',
         "admin/test_data/enroll-existing-participants.csv", False),
    )
    def test_csv_upload_views(self, view, file_key, test_file_path, is_valid):
        request = self.post_request('/dummy/',  self.admin_user)
        with open(test_file_path, "rb") as test_file:
            test_file = File(test_file)
            request.FILES.update({file_key: test_file})
            response = view(request)

            if is_valid:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn('task_key', response.content)
            else:
                self.assertEqual(response, None)


class UserDeleteTest(CourseParticipantsStatsMixin, TestCase):
    """
    Test user delete view.
    """

    def setUp(self):
        super(UserDeleteTest, self).setUp()
        self.patch_user_permissions()
        self.mock_id = 0
        delete_url = reverse('participant_details', kwargs={'user_id': self.mock_id})
        self.request = self.factory.delete(delete_url)
        self.request.user = self.admin_user
        self.api = views.participant_details_api()

    def test_delete_user_with_deletion_disabled(self):
        """
        Test deleting user without enabling `data_deletion.enable_data_deletion` waffle switch.
        """
        response = self.api.delete(self.request, self.mock_id)
        self.assertEqual(response.status_code, 400)

    @override_switch(get_deletion_waffle_switch(), active=True)
    @patch('lib.authorization.permission_group_required_not_in_group', lambda _: HttpResponseForbidden())
    def test_delete_user_without_permissions(self):
        """
        Test deleting user as non-admin user.
        """
        self.request.user = self.students[0]
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()

        response = self.api.delete(self.request, self.mock_id)
        self.assertEqual(response.status_code, 403)

    @override_switch(get_deletion_waffle_switch(), active=True)
    @patch('api_client.user_api.get_users', return_value=[])
    @patch('api_client.user_api.delete_users')
    def test_delete_nonexistent_user(self, delete_users_mock, get_users_mock):
        """
        Test deleting user that doesn't exist in LMS.
        """
        with self.assertRaises(Http404):
            self.api.delete(self.request, self.mock_id)

        get_users_mock.assert_called_with(ids=[str(self.mock_id)])
        delete_users_mock.assert_not_called()

    @override_switch(get_deletion_waffle_switch(), active=True)
    @patch('api_client.user_api.get_users', return_value=[MockUser(1), MockUser(2)])
    @patch('api_client.user_api.delete_users')
    def test_delete_user(self, *mocks):
        """
        Test deleting user as admin.
        """
        response = self.api.delete(self.request, self.mock_id)
        for mock in mocks:
            self.assertEqual(mock.call_count, 1)
        self.assertEqual(response.status_code, 204)


class ParticipantsListViewTest(CourseParticipantsStatsMixin, TestCase):
    """
    Test participants list view
    """
    @override_switch(get_deletion_waffle_switch(), active=True)
    def test_check_switch_on_view(self, *patch):
        """
        Test if waffle switch to enable deletion is correctly passed to the redered view
        """
        is_user_in_permission_group_lib = self.apply_patch("lib.authorization.is_user_in_permission_group")
        is_user_in_permission_group_lib.return_value = True
        is_user_in_permission_group_accounts = self.apply_patch("accounts.models.is_user_in_permission_group")
        is_user_in_permission_group_accounts.return_value = True
        is_user_in_permission_group_admin = self.apply_patch("admin.views.is_user_in_permission_group")
        is_user_in_permission_group_admin.return_value = True

        request = self.get_request(reverse('participants_list'), self.admin_user)
        response = views.participants_list(request)

        self.assertIn("var enable_data_deletion = 'True';", response.content)


@ddt.ddt
class ClientCustomizationTests(TestCase, ApplyPatchMixin):
    """
    Client Customization tests
    to enable / disable new UI
    """
    def setUp(self):
        super(ClientCustomizationTests, self).setUp()
        is_user_in_permission_group_lib = self.apply_patch("lib.authorization.is_user_in_permission_group")
        is_user_in_permission_group_lib.return_value = True
        is_user_in_permission_group_accounts = self.apply_patch("accounts.models.is_user_in_permission_group")
        is_user_in_permission_group_accounts.return_value = True

        self.client = make_company(1)
        self.admin_user = make_user(username="mcka_admin", email="mcka_admin@example.com")
        self.factory = RequestFactory()
        self.mock_session = Mock(session_key='', __contains__=lambda _a, _b: False)

    @ddt.data(True, False)
    def test_new_ui_flag_with_uber_admin(self, is_mcka_admin):
        """
        Test whether only uber admin can change the UI
        """
        client_customization = ClientCustomization.objects.create(client_id=self.client.id)
        request = self.factory.post(
            reverse('client_detail_navigation', kwargs={'client_id': self.client.id}),
            {'new_ui_enabled': 'on'}
        )
        self.admin_user.is_mcka_admin = is_mcka_admin
        request.user = self.admin_user
        request.session = self.mock_session
        update_mobile_customization = self.apply_patch("admin.views.update_mobile_client_detail_customization")
        update_mobile_customization.return_value = None
        response = views.client_detail_customization(request, self.client.id)
        client_customization.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        if is_mcka_admin:
            self.assertTrue(client_customization.new_ui_enabled)
        else:
            self.assertFalse(client_customization.new_ui_enabled)


class CompanyDetailsViewTest(CourseParticipantsStatsMixin, TestCase):
    """
    Test company details view.
    """

    def setUp(self):
        super(CompanyDetailsViewTest, self).setUp()
        self.patch_user_permissions()
        self.mock_id = 0
        delete_url = reverse('company_details', kwargs={'company_id': self.mock_id})
        self.request = self.factory.delete(delete_url)
        self.request.user = self.admin_user
        self.api = views.CompanyDetailsView()

    def test_delete_company_with_deletion_disabled(self):
        """
        Test deleting company without enabling `data_deletion.enable_data_deletion` waffle switch.
        """
        response = self.api.delete(self.request, self.mock_id)
        self.assertEqual(response.status_code, 400)

    @override_switch(get_deletion_waffle_switch(), active=True)
    @patch('lib.authorization.permission_group_required_not_in_group', lambda _: HttpResponseForbidden())
    def test_delete_company_without_permissions(self):
        """
        Test deleting company as non-admin company.
        """
        self.request.user = self.students[0]
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()

        response = self.api.delete(self.request, self.mock_id)
        self.assertEqual(response.status_code, 403)

    @override_switch(get_deletion_waffle_switch(), active=True)
    @patch('admin.controller.get_mobile_app_themes', lambda _: [])
    @patch('api_client.organization_api.fetch_organization_user_ids', return_value=[])
    @patch('api_client.organization_api.delete_organization', side_effect=Http404)
    def test_delete_nonexistent_company(self, *mocks):
        """
        Test deleting company that doesn't exist in LMS.
        """
        with self.assertRaises(Http404):
            self.api.delete(self.request, self.mock_id)

        for mock in mocks:
            mock.assert_called_with(self.mock_id)

    @override_switch(get_deletion_waffle_switch(), active=True)
    @patch('api_client.organization_api.delete_organization')
    @patch('admin.controller.remove_mobile_app_theme', side_effect=make_side_effect_raise_api_error(404))
    @patch('admin.views._delete_participants')
    @patch('api_client.organization_api.fetch_organization_user_ids')
    @patch('admin.controller.get_mobile_app_themes')
    def test_delete_company_race_condition(self, get_theme_mock, fetch_users_mock, *mocks):
        """
        Test deleting company with the race condition during removing mobile app theme.
        """
        get_theme_mock.return_value = [{'id': self.mock_id}]
        fetch_users_mock.return_value = [self.mock_id]

        response = self.api.delete(self.request, self.mock_id)
        for mock in mocks:
            self.assertEqual(mock.call_count, 1)

        self.assertEqual(response.status_code, 204)

    @override_switch(get_deletion_waffle_switch(), active=True)
    @patch('admin.controller.remove_mobile_app_theme')
    @patch('api_client.organization_api.delete_organization')
    @patch('admin.views._delete_participants')
    @patch('api_client.organization_api.fetch_organization_user_ids')
    @patch('admin.controller.get_mobile_app_themes')
    def test_delete_company(self, get_theme_mock, fetch_users_mock, *mocks):
        """
        Test deleting company as admin.
        """
        get_theme_mock.return_value = [{'id': self.mock_id}]
        fetch_users_mock.return_value = [self.mock_id]

        response = self.api.delete(self.request, self.mock_id)
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

        self.assertEqual(response.status_code, 204)


@ddt.ddt
class ProblemResponseReportViewTest(TestCase):
    """
    Test company details view.
    """

    @classmethod
    def setUpClass(cls):
        super(ProblemResponseReportViewTest, cls).setUpClass()
        AdminTask.objects.create(
            task_id='task_id1',
            course_id='course_id',
            parameters='{"problem_location": "problem_location"}',
            task_type='problem_response_report',
            output='',
            status='PROGRESS',
            username='username'
        )
        AdminTask.objects.create(
            task_id='task_id2',
            course_id='course_id1',
            parameters='{"problem_location": "problem_location"}',
            task_type='problem_response_report',
            output='',
            status='RETRYING',
            username='username'
        )
        AdminTask.objects.create(
            task_id='task_id3',
            course_id='course_id1',
            parameters='{"problem_location": "problem_location1"}',
            task_type='problem_response_report',
            output='{"url": "url", "name": "name"}',
            status='DONE',
            username='username'
        )
        AdminTask.objects.create(
            task_id='task_id4',
            course_id='course_id',
            parameters='{"problem_location": "problem_location"}',
            task_type='problem_response_report',
            output='{"url": "url", "name": "name"}',
            status='DONE',
            username='username'
        )

    def setUp(self):
        super(ProblemResponseReportViewTest, self).setUp()
        self.course_url = reverse(
            'course-reports',
            kwargs={'course_id': 'course_id'}
        )
        self.course_1_url = reverse(
            'course-reports',
            kwargs={'course_id': 'course_id1'}
        )
        self.course_2_url = reverse(
            'course-reports',
            kwargs={'course_id': 'course_id2'}
        )
        self.factory = APIRequestFactory()
        self.admin_user = make_user(username="mcka_admin", email="mcka_admin@example.com")
        self.admin_user.is_internal_admin = True
        self.admin_user.is_company_admin = False
        self.api = views.ProblemResponseReportView.as_view()
        self.in_progress_admin_task = Mock(spec=AdminTask)
        self.mock_session = Mock(session_key='', __contains__=lambda _a, _b: False)

    @classmethod
    def tearDownClass(cls):
        super(ProblemResponseReportViewTest, cls).tearDownClass()
        AdminTask.objects.all().delete()

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @ddt.data(True, False)
    @patch('admin.views.create_problem_response_report', new_callable=mock_task)
    @patch('admin.views.monitor_problem_response_report', new_callable=mock_task)
    @patch('admin.views.post_process_problem_response_report', new_callable=mock_task)
    @patch('admin.views.send_problem_response_report_success_email', new_callable=mock_task)
    def test_create_report_new(self, task_admin_create, *tasks):
        """Test create a new report."""
        if task_admin_create:
            count = AdminTask.objects.count() + 1
            request = self.factory.post(self.course_2_url, {'problem_location': 'problem_location'})
        else:
            count = AdminTask.objects.count()
            request = self.factory.post(self.course_1_url, {'problem_location': 'problem_location'})

        request.user = self.admin_user
        request.session = self.mock_session
        force_authenticate(request, user=self.admin_user)
        if task_admin_create:
            response = self.api(request, 'course_id2')
        else:
            response = self.api(request, 'course_id1')
        self.assertEqual(response.data['status'], 'OK')
        self.assertTrue(response.data['task_id'])
        self.assertEqual(AdminTask.objects.count(), count)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @ddt.data(True, False)
    @patch('admin.views.create_problem_response_report', new_callable=mock_task)
    @patch('admin.views.monitor_problem_response_report', new_callable=mock_task)
    @patch('admin.views.post_process_problem_response_report', new_callable=mock_task)
    @patch('admin.views.send_problem_response_report_success_email', new_callable=mock_task)
    def test_post_running_report(self, task_admin_running, *tasks):
        """Test should not create new report and only return a running report."""
        count = AdminTask.objects.count()
        if task_admin_running:
            request = self.factory.post(self.course_url, {'problem_location': 'problem_location'})
        else:
            request = self.factory.post(self.course_1_url, {'problem_location': 'problem_location'})

        request.user = self.admin_user
        request.session = self.mock_session
        force_authenticate(request, user=self.admin_user)
        if task_admin_running:
            response = self.api(request, 'course_id')
        else:
            response = self.api(request, 'course_id1')

        self.assertEqual(response.data['status'], 'OK')
        self.assertTrue(response.data['task_id'])
        self.assertEqual(AdminTask.objects.count(), count)

    def test_fetch_reports(self):
        """Fetch list of reports for a course"""
        request = self.factory.get(self.course_url)
        request.user = self.admin_user
        request.session = self.mock_session
        force_authenticate(request, user=self.admin_user)
        response = self.api(request, 'course_id')
        self.assertEqual(len(response.data['reports']), 2)
