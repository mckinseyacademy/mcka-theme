import datetime
import controller
import tempfile
import os
import math

from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.core.urlresolvers import resolve

from lib.util import DottableDict
from .forms import ClientForm, ProgramForm
from .models import Program
from .review_assignments import ReviewAssignmentProcessor, ReviewAssignmentUnattainableError

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Create your tests here.

# disable no-member 'cos the members are getting created from the json
# and some others that we don't care about for tests
# pylint: disable=no-member,line-too-long,too-few-public-methods,missing-docstring,too-many-public-methods,pointless-statement,unused-argument,protected-access,maybe-no-member,invalid-name

def test_user(id):
    return DottableDict({"id": id})

def test_workgroup(id, users):
    return DottableDict({"id": id, "users": users})

def test_set(num_users, workgroup_size):
    users = [test_user(i) for i in range(num_users)]
    workgroups = [test_workgroup(j, [u.id for u in users if int(math.floor(u.id/workgroup_size)) == j]) for j in range(int(math.ceil(num_users/workgroup_size)))]
    return users, workgroups

class ReviewAssignmentsTest(TestCase):

    def test_one_user_in_each_of_2_groups(self):
        ''' one user in each workgroup - should do each others '''
        users = [test_user(1), test_user(2)]
        workgroups = [test_workgroup(11, [1]), test_workgroup(12, [2])]

        rap = ReviewAssignmentProcessor(users, workgroups, 1)
        rap.distribute()

        self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
        self.assertEqual(rap.workgroup_reviewers[11][0], 2)

        self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
        self.assertEqual(rap.workgroup_reviewers[12][0], 1)

        with self.assertRaises(ReviewAssignmentUnattainableError):
            rap = ReviewAssignmentProcessor(users, workgroups, 2)
            rap.distribute()


    def test_one_user_in_each_of_3_groups(self):
        users = [test_user(1), test_user(2), test_user(3)]
        workgroups = [test_workgroup(11, [1]), test_workgroup(12, [2]), test_workgroup(13, [3])]

        rap = ReviewAssignmentProcessor(users, workgroups, 2)
        rap.distribute()

        self.assertEqual(len(rap.workgroup_reviewers[11]), 2)
        self.assertEqual(len(rap.workgroup_reviewers[12]), 2)
        self.assertEqual(len(rap.workgroup_reviewers[13]), 2)

        rap.workgroup_reviewers[11].sort()
        self.assertEqual(rap.workgroup_reviewers[11], [2,3])
        rap.workgroup_reviewers[12].sort()
        self.assertEqual(rap.workgroup_reviewers[12], [1,3])
        rap.workgroup_reviewers[13].sort()
        self.assertEqual(rap.workgroup_reviewers[13], [1,2])

        rap = ReviewAssignmentProcessor(users, workgroups, 1)
        rap.distribute()

        self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
        self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
        self.assertEqual(len(rap.workgroup_reviewers[13]), 1)

        self.assertTrue(rap.workgroup_reviewers[11] == [2] or rap.workgroup_reviewers[11] == [3])
        self.assertTrue(rap.workgroup_reviewers[12] == [1] or rap.workgroup_reviewers[12] == [3])
        self.assertTrue(rap.workgroup_reviewers[13] == [1] or rap.workgroup_reviewers[13] == [2])

        with self.assertRaises(ReviewAssignmentUnattainableError):
            rap = ReviewAssignmentProcessor(users, workgroups, 3)
            rap.distribute()


    def test_two_users_in_each_of_2_groups(self):
        users = [test_user(1), test_user(2), test_user(11), test_user(12)]
        workgroups = [test_workgroup(101, [1,11]), test_workgroup(102, [2,12])]

        rap = ReviewAssignmentProcessor(users, workgroups, 2)
        rap.distribute()

        self.assertEqual(len(rap.workgroup_reviewers[101]), 2)
        self.assertEqual(len(rap.workgroup_reviewers[102]), 2)
        rap.workgroup_reviewers[101].sort()
        self.assertEqual(rap.workgroup_reviewers[101], [2,12])
        rap.workgroup_reviewers[102].sort()
        self.assertEqual(rap.workgroup_reviewers[102], [1,11])

        with self.assertRaises(ReviewAssignmentUnattainableError):
            rap = ReviewAssignmentProcessor(users, workgroups, 3)
            rap.distribute()

    def test_lotsa_peeps(self):
        users, workgroups = test_set(200, 4)

        rap = ReviewAssignmentProcessor(users, workgroups, 10)
        rap.distribute()

        # Make sure all groups have 2 reviewers
        for wg in workgroups:
            self.assertTrue(len(rap.workgroup_reviewers[wg.id]) == 10)

        # Make sure that it is fairly even
        max_assignments = max([len(rap.reviewer_workgroups[u.id]) for u in users])
        min_assignments = min([len(rap.reviewer_workgroups[u.id]) for u in users])

        self.assertTrue(max_assignments - min_assignments < 2)

class UrlsTest(TestCase):

    def test_url_patterns(self):
        resolver = resolve('/admin/')
        self.assertEqual(resolver.view_name, 'admin_home')

        resolver = resolve('/admin/course-meta-content')
        self.assertEqual(resolver.view_name, 'course_meta_content_course_list')

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
            "contact_phone": "phone",
            "contact_email": "email@email.com",
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

    def test__build_student_list_from_file(self):
        # build temp file to fake stream to student list
        user_objects = []
        c = RequestFactory()
        test_file_path = os.path.join(BASE_DIR, 'admin/test_data/test_user_list.csv')
        with open(test_file_path) as test_file_content:
            request = c.post('/admin/clients/12345/upload_student_list', {'student_list': test_file_content})

        user_objects = controller._build_student_list_from_file(request.FILES['student_list'])
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

class ProgramTests(TestCase):

    def test_program(self):
        test_json = '{"name": "Maggie","uri": "http://localhost:56480/api/groups/39","resources": [{"uri": "http://localhost:56480/api/groups/39/users"}, {"uri": "http://localhost:56480/api/groups/39/groups"}],"data": {"display_name": "Maggie","start_date": "2014-1-1T00:00:00.00000Z","end_date": "2014-12-3T00:00:00.00000Z"},"id": 39,"group_type": "series"}'

        test_info = Program(test_json)

        self.assertEqual(test_info.name, "Maggie")
        self.assertEqual(test_info.display_name, "Maggie")
        self.assertEqual(test_info.start_date, datetime.datetime(2014,1,1))
        self.assertEqual(test_info.end_date, datetime.datetime(2014,12,3))
