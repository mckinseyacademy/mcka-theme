from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import resolve

from .forms import ClientForm, ProgramForm
import datetime

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

        resolver = resolve('/admin/clients/XYXYZ')
        self.assertEqual(resolver.view_name, 'client_detail')
        self.assertEqual(resolver.kwargs['client_id'], 'XYXYZ')

        resolver = resolve('/admin/clients')
        self.assertEqual(resolver.view_name, 'client_list')

        resolver = resolve('/admin/programs/program_new')
        self.assertEqual(resolver.view_name, 'program_new')

        resolver = resolve('/admin/programs/XYXYZ')
        self.assertEqual(resolver.view_name, 'program_detail')
        self.assertEqual(resolver.kwargs['program_id'], 'XYXYZ')

        resolver = resolve('/admin/programs')
        self.assertEqual(resolver.view_name, 'program_list')

class AdminFormsTests(TestCase):
    ''' Test Admin Forms '''

    def test_ClientForm(self):
        # valid if data is good
        client_data = {
            "name": "company",
            "contact_name": "contact_name",
            "phone": "phone",
            "email": "email",
        }
        client_form = ClientForm(client_data)

        self.assertTrue(client_form.is_valid())

    def test_ProgramForm(self):
        # valid if data is good
        program_data = {
            "name": "public_name",
            "private_name": "private_name",
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
