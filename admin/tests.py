from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.core.urlresolvers import resolve

from .forms import ClientForm, ProgramForm
import datetime
import controller
import tempfile

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Create your tests here.

# disable no-member 'cos the members are getting created from the json
# and some others that we don't care about for tests
# pylint: disable=no-member,line-too-long,too-few-public-methods,missing-docstring,too-many-public-methods,pointless-statement,unused-argument,protected-access,maybe-no-member,invalid-name

class UrlsTest(TestCase):

    def test_url_patterns(self):
        resolver = resolve('/admin/')
        self.assertEqual(resolver.view_name, 'admin_home')

        resolver = resolve('/admin/course_meta_content')
        self.assertEqual(resolver.view_name, 'course_meta_content')

        resolver = resolve('/admin/not_authorized')
        self.assertEqual(resolver.view_name, 'not_authorized')

        resolver = resolve('/admin/clients/client_new')
        self.assertEqual(resolver.view_name, 'client_new')

        resolver = resolve('/admin/clients/12345')
        self.assertEqual(resolver.view_name, 'client_detail')
        self.assertEqual(resolver.kwargs['client_id'], '12345')

        resolver = resolve('/admin/clients/12345/upload_student_list')
        self.assertEqual(resolver.view_name, 'upload_student_list')
        self.assertEqual(resolver.kwargs['client_id'], '12345')

        resolver = resolve('/admin/clients/12345/download_student_list')
        self.assertEqual(resolver.view_name, 'download_student_list')
        self.assertEqual(resolver.kwargs['client_id'], '12345')

        resolver = resolve('/admin/clients/12345/program_association')
        self.assertEqual(resolver.view_name, 'program_association')
        self.assertEqual(resolver.kwargs['client_id'], '12345')

        resolver = resolve('/admin/clients/12345/add_students_to_program')
        self.assertEqual(resolver.view_name, 'add_students_to_program')
        self.assertEqual(resolver.kwargs['client_id'], '12345')

        resolver = resolve('/admin/clients/12345/add_students_to_course')
        self.assertEqual(resolver.view_name, 'add_students_to_course')
        self.assertEqual(resolver.kwargs['client_id'], '12345')

        resolver = resolve('/admin/clients/12345/other_named_detail')
        self.assertEqual(resolver.view_name, 'client_detail')
        self.assertEqual(resolver.kwargs['client_id'], '12345')
        self.assertEqual(resolver.kwargs['detail_view'], 'other_named_detail')

        resolver = resolve('/admin/clients')
        self.assertEqual(resolver.view_name, 'client_list')

        resolver = resolve('/admin/programs/program_new')
        self.assertEqual(resolver.view_name, 'program_new')

        resolver = resolve('/admin/programs/987')
        self.assertEqual(resolver.view_name, 'program_detail')
        self.assertEqual(resolver.kwargs['program_id'], '987')

        resolver = resolve('/admin/programs/987/add_courses')
        self.assertEqual(resolver.view_name, 'add_courses')
        self.assertEqual(resolver.kwargs['program_id'], '987')

        resolver = resolve('/admin/programs/987/download_program_report')
        self.assertEqual(resolver.view_name, 'download_program_report')
        self.assertEqual(resolver.kwargs['program_id'], '987')

        resolver = resolve('/admin/programs/987/other_named_detail')
        self.assertEqual(resolver.view_name, 'program_detail')
        self.assertEqual(resolver.kwargs['program_id'], '987')
        self.assertEqual(resolver.kwargs['detail_view'], 'other_named_detail')

        resolver = resolve('/admin/programs')
        self.assertEqual(resolver.view_name, 'program_list')



class AdminFormsTests(TestCase):
    ''' Test Admin Forms '''

    def test_ClientForm(self):
        # valid if data is good
        client_data = {
            "display_name": "company",
            "contact_name": "contact_name",
            "phone": "phone",
            "email": "email",
        }
        client_form = ClientForm(client_data)

        self.assertTrue(client_form.is_valid())

    def test_ProgramForm(self):
        # valid if data is good
        program_data = {
            "display_name": "public_name",
            "name": "private_name",
            "start_date": datetime.datetime(2014, 1, 1),
            "end_date": datetime.datetime(2014, 12, 12),
        }
        program_form = ProgramForm(program_data)

        self.assertTrue(program_form.is_valid())

# class AdminViewsTests(TestCase):

#     def test_home_fail(self):
#         c = Client()
#         response = c.get('/admin/')
#         self.assertEqual(response.status_code, 302)
#         self.assertTrue(response.content.find("unauthorized") > -1)

#     # def test_home_okay(self):
#     #     c = Client()
#     #     # c.login(username='gooduser', password='password')
#     #     response = c.get('/admin/')
#     #     self.assertEqual(response.status_code, 200)

class AdminControllerTests(TestCase):

    def test__process_line(self):
        # format is email,username,password,firstname,lastname
        test_line = "email@testorg.org,test_user,test_password,Test,User"
        user_info = controller._process_line(test_line)
        self.assertEqual(user_info["email"], "email@testorg.org")
        self.assertEqual(user_info["username"], "test_user")
        self.assertEqual(user_info["password"], "test_password")
        self.assertEqual(user_info["first_name"], "Test")
        self.assertEqual(user_info["last_name"], "User")

        test_line = "email@testorg.org,test_user,test_password"
        user_info = controller._process_line(test_line)
        self.assertEqual(user_info["email"], "email@testorg.org")
        self.assertEqual(user_info["username"], "test_user")
        self.assertEqual(user_info["password"], "test_password")
        self.assertFalse("first_name" in user_info)
        self.assertFalse("last_name" in user_info)

    def test__build_student_list_from_file(self):
        # build temp file to fake stream to student list
        user_objects = []
        c = RequestFactory()
        test_file_path = os.path.join(BASE_DIR, 'admin/test_data/test_user_list.csv')
        with open(test_file_path) as test_file_content:
            request = c.post('/admin/clients/12345/upload_student_list', {'student_list': test_file_content})

        user_objects = controller._build_student_list_from_file(request.FILES['student_list'])
        self.assertEqual(len(user_objects), 3)

        self.assertEqual(user_objects[0]["email"], "email@testorg.org")
        self.assertEqual(user_objects[0]["username"], "test_user")
        self.assertEqual(user_objects[0]["password"], "test_password")
        self.assertEqual(user_objects[0]["first_name"], "Test")
        self.assertEqual(user_objects[0]["last_name"], "User")
        
        self.assertEqual(user_objects[1]["email"], "email2@testorg.org")
        self.assertEqual(user_objects[1]["username"], "test_user2")
        self.assertEqual(user_objects[1]["password"], "test_password")
        self.assertFalse("first_name" in user_objects)
        self.assertFalse("last_name" in user_objects)

        self.assertEqual(user_objects[2]["email"], "email3@testorg.org")
        self.assertEqual(user_objects[2]["username"], "test_user3")
        self.assertEqual(user_objects[2]["password"], "test_password")
        self.assertEqual(user_objects[2]["first_name"], "Test3")
        self.assertEqual(user_objects[2]["last_name"], "User3")
