import os
import ddt
import csv

from django.http import HttpResponse
from django.test.client import RequestFactory
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

import admin.controller as controller
from accounts.tests.utils import ApplyPatchMixin
from admin.controller import CourseParticipantStats, create_roles_list, write_participant_performance_on_csv,\
    write_engagement_summary_on_csv, write_social_engagement_report_on_csv, get_course_stats_report
from admin.models import SelfRegistrationRoles, CourseRun
from courses.models import FeatureFlags
from admin.tests.utils import BASE_DIR
from api_client.json_object import JsonParser as JP
from rest_framework import status
from api_client.json_object import JsonObject
from api_client import user_models


class AdminControllerTests(TestCase):
    def test__process_line(self):
        # format is email,username,password,firstname,lastname
        test_line = "email@testorg.org,Test,User,Hot-Dog Cart Guy,Cambridge,US"
        user_info = controller._process_line(test_line)
        self.assertEqual(user_info["email"], "email@testorg.org")
        self.assertEqual(user_info["first_name"], "Test")
        self.assertEqual(user_info["last_name"], "User")
        self.assertEqual(user_info["title"], "Hot-Dog Cart Guy")
        self.assertEqual(user_info["city"], "Cambridge")
        self.assertEqual(user_info["country"], "US")

        test_line = "email@testorg.org,Test,User"
        user_info = controller._process_line(test_line)
        self.assertEqual(user_info["email"], "email@testorg.org")
        self.assertEqual(user_info["first_name"], "Test")
        self.assertEqual(user_info["last_name"], "User")
        self.assertFalse("title" in user_info)
        self.assertFalse("city" in user_info)
        self.assertFalse("country" in user_info)

    def test_build_student_list_from_file(self):
        # build temp file to fake stream to student list
        user_objects = []
        c = RequestFactory()
        test_file_path = os.path.join(BASE_DIR, 'test_data/test_user_list.csv')
        with open(test_file_path) as test_file_content:
            request = c.post('/admin/clients/12345/upload_student_list', {'student_list': test_file_content})

        user_objects = controller.build_student_list_from_file(request.FILES['student_list'])
        self.assertEqual(len(user_objects), 4)

        self.assertEqual(user_objects[0]["email"], "email1@testorg.org")
        self.assertEqual(user_objects[0]["first_name"], "Test1")
        self.assertEqual(user_objects[0]["last_name"], "User1")
        self.assertFalse("title" in user_objects[0])
        self.assertFalse("city" in user_objects[0])
        self.assertFalse("country" in user_objects[0])

        self.assertEqual(user_objects[1]["email"], "email2@testorg.org")
        self.assertEqual(user_objects[1]["first_name"], "Test2")
        self.assertEqual(user_objects[1]["last_name"], "User2")
        self.assertEqual(user_objects[1]["title"], "Director Of Engineering")
        self.assertFalse("city" in user_objects[1])
        self.assertFalse("country" in user_objects[1])

        self.assertEqual(user_objects[2]["email"], "email3@testorg.org")
        self.assertEqual(user_objects[2]["first_name"], "Test3")
        self.assertEqual(user_objects[2]["last_name"], "User3")
        self.assertEqual(user_objects[2]["title"], "Dogwalker")
        self.assertEqual(user_objects[2]["city"], "Cambridge")
        self.assertFalse("country" in user_objects[1])

        self.assertEqual(user_objects[3]["email"], "email4@testorg.org")
        self.assertEqual(user_objects[3]["first_name"], "Test4")
        self.assertEqual(user_objects[3]["last_name"], "User4")
        self.assertEqual(user_objects[3]["title"], "Hot-Dog Cart Guy")
        self.assertEqual(user_objects[3]["city"], "Cambridge")
        self.assertEqual(user_objects[3]["country"], "US")


def MockEngagementScore(object):
    data = {
        'users':
            {
                '1':
                    {
                        'num_threads': 1,
                        'num_comments': 1,
                        'num_replies': 1,
                        'num_upvotes': 1,
                        'num_thread_followers': 1,
                        'num_comments_generated': 1,
                    },
                '2':
                    {
                        'num_threads': 2,
                        'num_comments': 1,
                        'num_replies': 0,
                        'num_upvotes': 0,
                        'num_thread_followers': 0,
                        'num_comments_generated': 0,
                    }
            }
    }

    return JP.from_dictionary(data)


class TestsCourseParticipantStats(TestCase, ApplyPatchMixin):
    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_get_engagement_scores(self):
        self.apply_patch('api_client.course_api.get_course_social_metrics', new=MockEngagementScore)
        test_object = CourseParticipantStats('1', 'base/url')
        u_ids = ['1', '2']
        engagement_scores = test_object._get_engagement_scores()
        self.assertEqual(engagement_scores[u_ids[0]], 85)
        self.assertEqual(engagement_scores[u_ids[1]], 35)


@ddt.ddt
class EditSelfRoleRegistrationTests(TestCase):

    def setUp(self):

        course_run = CourseRun.objects.create(
            name="abc", course_id="abc", email_template_new="email", email_template_existing="email",
            email_template_mcka="email", email_template_closed="email", self_registration_page_heading="abc",
            self_registration_description_text="abc")
        self.self_reg_role = SelfRegistrationRoles.objects.create(option_text="abc", course_run_id=course_run)

    @ddt.data(
        ("role", status.HTTP_200_OK, "Operation Successful"),
        ("", status.HTTP_404_NOT_FOUND, "Please enter role text"),
    )
    @ddt.unpack
    def edit_self_role_registration_validation(self, role_text, status, msg):

        status_code, message = controller.edit_self_register_role(self.self_reg_role.id, role_text)
        self.assertEqual(status_code, status)
        self.assertEqual(message, msg)

    @ddt.data(
        (100, "role", status.HTTP_404_NOT_FOUND, "Sorry, We can not process your request"),
    )
    @ddt.unpack
    def edit_self_role_registration_fail(self, role_id, role_text, status, msg):

        status_code, message = controller.edit_self_register_role(role_id, role_text)
        self.assertEqual(status, status)
        self.assertEqual(message, msg)

    def delete_self_role_registration_success(self):

        status_code, message = controller.delete_self_reg_role(self.self_reg_role.id)
        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(message, "Operation Successful")

    def delete_self_role_registration_fail(self):

        status_code, message = controller.delete_self_reg_role(100)
        self.assertEqual(status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(message, "Sorry, We can not process your request")


class RemoveRoleRegistrationTests(TestCase):

    def setUp(self):
        course_run = CourseRun.objects.create(
            name="abc", course_id="abc", email_template_new="email", email_template_existing="email",
            email_template_mcka="email", email_template_closed="email", self_registration_page_heading="abc",
            self_registration_description_text="abc")
        self.self_reg_role = SelfRegistrationRoles.objects.create(option_text="abc", course_run_id=course_run)

    def delete_self_role_registration_success(self):

        status_code, message = controller.delete_self_reg_role(self.self_reg_role.id)
        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(message, "Operation Successful")

    def delete_self_role_registration_fail(self):

        status_code, message = controller.delete_self_reg_role(100)
        self.assertEqual(status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(message, "Sorry, We can not process your request")


class TestCreateRolesList(TestCase):
    """Test the method create_roles_list from admin/controller.py"""
    def setUp(self):
        self.factory = RequestFactory()

    def test_with_valid_input(self):
        """test with valid input passes the RoleTileValidator"""
        data = {
            'role': 'Seasoned Leader/Senior Manager (e.g., VP, Director)',
            'role2': 'Early Career Professional (e.g., Associate, Analyst)',
            'extra': 'extra'
        }
        request = self.factory.post('/', data)
        roles = create_roles_list(request)
        self.assertEquals(roles, ['Seasoned Leader/Senior Manager (e.g., VP, Director)',
                                  'Early Career Professional (e.g., Associate, Analyst)'])

    def test_with_invalid_input(self):
        """test with invalid input which raises validation error"""
        data = {
            'role': '{Seasoned Leader/Senior Manager} (e.g., VP, Director)',
            'role2': '%$Early Career Professional (e.g., Associate, Analyst)',
            'extra': 'extra'
        }
        request = self.factory.post('/', data)
        with self.assertRaises(ValidationError):
            roles = create_roles_list(request)


class TestGetCourseStatsReport(TestCase, ApplyPatchMixin):
    social_stats = [
        {"name": "test1", "value": "test value"},
        {"name": "test2", "value": "1234567799"},
        {"name": "test3", "value": "test 12345"},
    ]

    engagement_stats = [
        {"name": "test1", "people": 40, "invited": 0, "progress": 100},
        {"name": "test2", "people": 00, "invited": 10, "progress": 66},
    ]

    expected_result_for_social = '\r\nSocial Engagement,#\r\ntest1,test value' \
                                 '\r\ntest2,1234567799\r\ntest3,test 12345\r\n'

    expected_result_for_summary = 'Engagement Summary,# of people,% total cohort,' \
                                  'Avg Progress\r\ntest1,40,0,100\r\ntest2,0,10,66\r\n'

    expected_result_for_perfromance = '\r\nParticipant Performance,% completion,Score' \
                                      '\r\nGroup work 1,-,-\r\nGroup work 2,-,-\r\nMid-course' \
                                      ' assessment,-,-\r\nFinal assessment,-,-\r\n'

    def setUp(self):
        engagement_function = 'admin.controller.get_course_social_engagement'
        engagement_summary_function = 'admin.controller.get_course_engagement_summary'

        self.social_engagement = self.apply_patch(engagement_function)
        self.engagement_summary = self.apply_patch(engagement_summary_function)

        self.social_engagement.return_value = self.social_stats
        self.engagement_summary.return_value = self.engagement_stats

    def test_write_social_engagement_report_on_csv(self):
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)

        write_social_engagement_report_on_csv(writer, "123", "123")
        self.assertEqual(self.expected_result_for_social, response.content)

    def test_write_engagement_summary_on_csv(self):
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)

        write_engagement_summary_on_csv(writer, "123", "123")
        self.assertEqual(self.expected_result_for_summary, response.content)

    def test_write_participant_performance_on_csv(self):
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)

        write_participant_performance_on_csv(writer)
        self.assertEqual(self.expected_result_for_perfromance, response.content)

    def test_get_course_stats_report(self):
        course_api = self.apply_patch('api_client.course_api.get_course_details')
        course_api.return_value = {"name": "test_course"}
        response = get_course_stats_report("test_company", "test_Course")
        expected_result = self.expected_result_for_summary + self.expected_result_for_perfromance\
            + self.expected_result_for_social

        self.assertEqual(response.content, expected_result)
        course_features = FeatureFlags.objects.get(course_id="test_course")
        course_features.discussions = False
        course_features.save()

        response = get_course_stats_report("test_company", "test_Course")
        expected_result = self.expected_result_for_summary + self.expected_result_for_perfromance

        self.assertEqual(response.content, expected_result)


class TestContactsForClient(TestCase, ApplyPatchMixin):
    def setUp(self):
        # Mocking Apis for the method
        self.organization_api = self.apply_patch('api_client.organization_models.organization_api')
        self.group_api = self.apply_patch('admin.controller.group_api')
        self.user_api = self.apply_patch('admin.controller.user_api')

    def test_get_contacts_for_client(self):
        # Dummy Data for the Apis
        client_id = '2'
        client_groups_data = '[{"id": 12,"type": "contact_group","data": {}}]'
        client_groups_users_data = '{"users": [{"id": 3, "email": "audit@example.com", "username": "audit"},' \
                                   '{"id": 10, "email": "test@example.com", "username": "test"}]}'
        client_groups_user_profile_data = '[{"id": 3, "email": "audit@example.com","username": "audit"},' \
                                          '{"id": 10, "email": "test@example.com","username": "test"}]'
        # Mocking Api Calls
        self.organization_api.get_organization_groups.return_value = JP.from_json(client_groups_data, JsonObject)
        self.group_api.get_users_in_group.return_value = JP.from_json(client_groups_users_data,
                                                                      user_models.UserList).users
        self.user_api.get_users.return_value = JP.from_json(client_groups_user_profile_data, user_models.UserResponse)

        contacts = controller.get_contacts_for_client(client_id)

        self.assertEqual(contacts[0].email, "audit@example.com")
        self.assertEqual(contacts[1].email, "test@example.com")

    def test_get_contacts_for_client_with_no_contact(self):
        client_id = '2'
        client_groups_data = '[]'

        # Mocking Api Calls
        self.organization_api.get_organization_groups.return_value = JP.from_json(client_groups_data, JsonObject)

        contacts = controller.get_contacts_for_client(client_id)
        self.assertEqual(contacts, [])


class TestSpecificUserRolesOfOtherCompanies(TestCase):

    def test_remove_specific_user_roles_of_other_companies(self):
        organization_id = '7'
        course_participants = {u'count': 4, u'previous': None, u'num_pages': 1, u'results':
            [
            {'username': 'UAdmin_user',
             'roles': ['observer'], 'organizations': [
                {'display_name': 'CompanyA', 'id': 6},
                {'display_name': 'CompanyB','id': 7}]},
            {'username': 'Cadmin', 'roles': [], 'organizations': [
                {'display_name': 'CompanyB','id': 7}]},
            {'username': 'companyB_TA',
             'roles': ['observer'],
              'organizations': [
                {'display_name': 'CompanyB',u'id': 7}]},
            {'username': 'uberadmin2',
             'roles': ['assistant'],'organizations': [
                {'id': 6},
                ]},
                {'username': 'uberadmin3',
                 'roles': ['participant'], 'organizations': [
                    {'id': 6},
                ]}
            ], 'next': None}

        course_participants = controller.remove_specific_user_roles_of_other_companies(course_participants,
                                                                                      int(organization_id))
        self.assertEqual(len(course_participants["results"]), 3)