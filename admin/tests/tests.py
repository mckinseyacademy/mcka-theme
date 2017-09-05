import datetime
import admin.controller as controller
import tempfile
import os
import math

from django.forms import ValidationError
from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.core.urlresolvers import resolve

from lib.util import DottableDict
from admin.forms import ClientForm, ProgramForm, CreateAccessKeyForm, ShareAccessKeyForm, MultiEmailField
from admin.models import Program
from admin.review_assignments import ReviewAssignmentProcessor, ReviewAssignmentUnattainableError

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Create your tests here.

# disable no-member 'cos the members are getting created from the json
# and some others that we don't care about for tests
# pylint: disable=no-member,line-too-long,too-few-public-methods,missing-docstring,too-many-public-methods,pointless-statement,unused-argument,protected-access,maybe-no-member,invalid-name

def test_user(id):
    return DottableDict({"id": id, "name": "test_user_{}".format(id)})

def test_workgroup(id, users):
    user_ids = []
    for user in users:
        user_ids.append(user.id)
    return DottableDict({"id": id, "users": users, "user_ids": user_ids})

def test_set(num_users, workgroup_size):
    users = [test_user(i) for i in range(num_users)]
    workgroups = [test_workgroup(j, [u for u in users if int(math.floor(u.id/workgroup_size)) == j]) for j in range(int(math.ceil(num_users/workgroup_size)))]
    return users, workgroups

class MockUser(object):

    id = None
    def __init__(self, user_id):
        self.id = user_id

class MockReviewAssignmentGroup(object):
    id = "fake_id"

    def __init__(self, workgroup, xblock_id):
        self.workgroups = []
        self.users = []
        self.xblock_id = xblock_id

        self.add_workgroup(workgroup.id)
        MockReviewAssignmentGroupCollection.workgroup_lookup[workgroup.id] = [self]

    def add_workgroup(self, workgroup):
        self.workgroups.append(workgroup)

    def add_user(self, user_id):
        self.users.append(MockUser(user_id))

    def get_users(self):
        return self.users

    @classmethod
    def list_for_workgroup(cls, workgroup_id, xblock_id=None):
        review_assignment_groups = MockReviewAssignmentGroupCollection.workgroup_lookup.get(workgroup_id, [])
        if xblock_id:
            review_assignment_groups = [rag for rag in review_assignment_groups if rag.xblock_id == xblock_id]
        return review_assignment_groups

    @classmethod
    def delete(cls, group_id):
        # will only get called when deleting everything, so for mock okay to just reset complete list
        MockReviewAssignmentGroupCollection.workgroup_lookup = {}

class MockReviewAssignmentGroupCollection(object):

    workgroup_lookup = {}

    @classmethod
    def load(cls, review_assignment_processor):
        cls.workgroup_lookup = {}
        for wg in review_assignment_processor.workgroups:
            rag = MockReviewAssignmentGroup(wg, review_assignment_processor.xblock_id)
            for user_id in review_assignment_processor.workgroup_reviewers[wg.id]:
                rag.add_user(user_id)


class ReviewAssignmentsTest(TestCase):

    def test_one_user_in_each_of_2_groups(self):
        ''' one user in each workgroup - should do each others '''
        test_user_1 = test_user(1)
        test_user_2 = test_user(2)
        users = [test_user_1, test_user_2]
        workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2])]

        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
        rap.distribute()

        self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
        self.assertEqual(rap.workgroup_reviewers[11][0], 2)

        self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
        self.assertEqual(rap.workgroup_reviewers[12][0], 1)

        with self.assertRaises(ReviewAssignmentUnattainableError):
            rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 2, 0)
            rap.distribute()

    def test_one_user_in_each_of_2_groups_with_min_users(self):
        ''' one user in each workgroup - should do each others '''
        test_user_1 = test_user(1)
        test_user_2 = test_user(2)
        users = [test_user_1, test_user_2]
        workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2])]

        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 1)
        rap.distribute()

        self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
        self.assertEqual(rap.workgroup_reviewers[11][0], 2)

        self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
        self.assertEqual(rap.workgroup_reviewers[12][0], 1)

        with self.assertRaises(ReviewAssignmentUnattainableError):
            rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 2)
            rap.distribute()


    def test_one_user_in_each_of_3_groups(self):
        test_user_1 = test_user(1)
        test_user_2 = test_user(2)
        test_user_3 = test_user(3)
        users = [test_user_1, test_user_2, test_user_3]
        workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2]), test_workgroup(13, [test_user_3])]

        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 2, 0)
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

        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
        rap.distribute()

        self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
        self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
        self.assertEqual(len(rap.workgroup_reviewers[13]), 1)

        self.assertTrue(rap.workgroup_reviewers[11] == [2] or rap.workgroup_reviewers[11] == [3])
        self.assertTrue(rap.workgroup_reviewers[12] == [1] or rap.workgroup_reviewers[12] == [3])
        self.assertTrue(rap.workgroup_reviewers[13] == [1] or rap.workgroup_reviewers[13] == [2])

        with self.assertRaises(ReviewAssignmentUnattainableError):
            rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 3, 0)
            rap.distribute()

    def test_one_user_in_each_of_3_groups_with_min_users(self):
        test_user_1 = test_user(1)
        test_user_2 = test_user(2)
        test_user_3 = test_user(3)
        users = [test_user_1, test_user_2, test_user_3]
        workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2]), test_workgroup(13, [test_user_3])]

        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 2)
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

        with self.assertRaises(ReviewAssignmentUnattainableError):
            rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 3)
            rap.distribute()

    def test_two_users_in_each_of_2_groups(self):
        test_user_1 = test_user(1)
        test_user_2 = test_user(2)
        test_user_11 = test_user(11)
        test_user_12 = test_user(12)
        users = [test_user_1, test_user_2, test_user_11, test_user_12]
        workgroups = [test_workgroup(101, [test_user_1, test_user_11]), test_workgroup(102, [test_user_2, test_user_12])]

        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 2, 0)
        rap.distribute()

        self.assertEqual(len(rap.workgroup_reviewers[101]), 2)
        self.assertEqual(len(rap.workgroup_reviewers[102]), 2)
        rap.workgroup_reviewers[101].sort()
        self.assertEqual(rap.workgroup_reviewers[101], [2,12])
        rap.workgroup_reviewers[102].sort()
        self.assertEqual(rap.workgroup_reviewers[102], [1,11])

        with self.assertRaises(ReviewAssignmentUnattainableError):
            rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 3, 0)
            rap.distribute()

    def test_two_users_in_each_of_2_groups_with_min_users(self):
        test_user_1 = test_user(1)
        test_user_2 = test_user(2)
        test_user_11 = test_user(11)
        test_user_12 = test_user(12)
        users = [test_user_1, test_user_2, test_user_11, test_user_12]
        workgroups = [test_workgroup(101, [test_user_1, test_user_11]), test_workgroup(102, [test_user_2, test_user_12])]

        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 0, 1)
        rap.distribute()

        self.assertEqual(len(rap.workgroup_reviewers[101]), 2)
        self.assertEqual(len(rap.workgroup_reviewers[102]), 2)
        rap.workgroup_reviewers[101].sort()
        self.assertEqual(rap.workgroup_reviewers[101], [2,12])
        rap.workgroup_reviewers[102].sort()
        self.assertEqual(rap.workgroup_reviewers[102], [1,11])

        with self.assertRaises(ReviewAssignmentUnattainableError):
            rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 0, 2)
            rap.distribute()

    def test_lotsa_peeps(self):
        users, workgroups = test_set(200, 4)

        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 10, 0)
        rap.distribute()

        # Make sure all groups have 10 reviewers
        for wg in workgroups:
            self.assertTrue(len(rap.workgroup_reviewers[wg.id]) == 10)

        # Make sure that it is fairly even
        max_assignments = max([len(rap.reviewer_workgroups[u.id]) for u in users])
        min_assignments = min([len(rap.reviewer_workgroups[u.id]) for u in users])

        self.assertTrue(max_assignments - min_assignments < 2)

    def test_lotsa_peeps_with_min_users(self):
        users, workgroups = test_set(200, 4)

        for i in range(3):
            rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, i)
            rap.distribute()

            # Make sure that all users have at least i reviews to perform
            min_assignments = min([len(rap.reviewer_workgroups[u.id]) for u in users])
            self.assertTrue(min_assignments >= i)

            # Make sure that it is fairly even
            max_assignments = max([len(rap.reviewer_workgroups[u.id]) for u in users])
            self.assertTrue(max_assignments - min_assignments < 2)

    def test_lotsa_peeps_with_min_users_unattainable(self):
        users, workgroups = test_set(200, 4)

        # largest attainable
        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 0, 49)
        rap.distribute()

        # Make sure that all users have at least i reviews to perform
        min_assignments = min([len(rap.reviewer_workgroups[u.id]) for u in users])
        max_assignments = max([len(rap.reviewer_workgroups[u.id]) for u in users])
        self.assertTrue(min_assignments == 49)
        self.assertTrue(max_assignments == 49)

        with self.assertRaises(ReviewAssignmentUnattainableError):
            rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 0, 50)
            rap.distribute()

    def test_assignment_twice(self):
        ''' one user in each workgroup - should do each others '''
        test_user_1 = test_user(1)
        test_user_2 = test_user(2)
        users = [test_user_1, test_user_2]
        workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2])]

        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
        rap.distribute()

        self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
        self.assertEqual(rap.workgroup_reviewers[11][0], 2)

        self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
        self.assertEqual(rap.workgroup_reviewers[12][0], 1)

        MockReviewAssignmentGroupCollection.load(rap)

        test_user_3 = test_user(3)
        test_user_4 = test_user(4)
        users.extend([test_user_3,test_user_4])
        workgroups.extend([test_workgroup(13, [test_user_3]), test_workgroup(14, [test_user_4])])

        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
        rap.distribute(False, assignment_group_class=MockReviewAssignmentGroup)

        # should be exactly the same as before for 11 and 12
        self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
        self.assertEqual(rap.workgroup_reviewers[11][0], 2)

        self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
        self.assertEqual(rap.workgroup_reviewers[12][0], 1)

        # and similarly, need new assignments for 13 and 14
        self.assertEqual(len(rap.workgroup_reviewers[13]), 1)
        self.assertEqual(rap.workgroup_reviewers[13][0], 4)

        self.assertEqual(len(rap.workgroup_reviewers[14]), 1)
        self.assertEqual(rap.workgroup_reviewers[14][0], 3)

        MockReviewAssignmentGroupCollection.load(rap)

        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
        rap.distribute(True, assignment_group_class=MockReviewAssignmentGroup)

        # should be exactly the same as before for 11 and 12
        self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
        self.assertFalse(rap.workgroup_reviewers[11][0] == 1)

        self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
        self.assertFalse(rap.workgroup_reviewers[12][0] == 2)

        # and similarly, need new assignments for 13 and 14
        self.assertEqual(len(rap.workgroup_reviewers[13]), 1)
        self.assertFalse(rap.workgroup_reviewers[13][0] == 3)

        self.assertEqual(len(rap.workgroup_reviewers[14]), 1)
        self.assertFalse(rap.workgroup_reviewers[14][0] == 4)

    def test_assignment_thrice(self):
        ''' one user in each workgroup - should do each others '''
        test_user_1 = test_user(1)
        test_user_2 = test_user(2)
        users = [test_user_1, test_user_2]
        workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2])]

        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
        rap.distribute()

        self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
        self.assertEqual(rap.workgroup_reviewers[11][0], 2)

        self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
        self.assertEqual(rap.workgroup_reviewers[12][0], 1)

        MockReviewAssignmentGroupCollection.load(rap)
        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
        rap.distribute(False, assignment_group_class=MockReviewAssignmentGroup)

        self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
        self.assertEqual(rap.workgroup_reviewers[11][0], 2)

        self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
        self.assertEqual(rap.workgroup_reviewers[12][0], 1)

        MockReviewAssignmentGroupCollection.load(rap)
        rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
        rap.distribute(False, assignment_group_class=MockReviewAssignmentGroup)

        self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
        self.assertEqual(rap.workgroup_reviewers[11][0], 2)

        self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
        self.assertEqual(rap.workgroup_reviewers[12][0], 1)

    def test_assignment_with_two_activities(self):
        ''' one user in each workgroup - should do each others '''
        test_user_1 = test_user(1)
        test_user_2 = test_user(2)
        users = [test_user_1, test_user_2]
        workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2])]

        '''Generate activity review assignment for test-activity-xblock-1 activity'''
        rap_assignment1 = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-activity-xblock-1', 1, 0)
        rap_assignment1.distribute(False, assignment_group_class=MockReviewAssignmentGroup)
        MockReviewAssignmentGroupCollection.load(rap_assignment1)

        '''
        There should be one assignment for test activity xblock 1 and workgroup 11
        There should be no assignments for test activity xblock 1 and workgroup 13 (workgroup doesn't exist)
        There should be no assignments for test activity xblock 2 and workgroup 12 (activity doesn't exist)
        There should be no assignments for test activity xblock 3 and workgroup 13 (both doesn't exist)
        '''
        self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(11, 'test-activity-xblock-1')), 1)
        self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(13, 'test-activity-xblock-1')), 0)
        self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(12, 'test-activity-xblock-2')), 0)
        self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(13, 'test-activity-xblock-3')), 0)

        '''Generate activity review assignment for test-activity-xblock-2 activity'''
        rap_assignment2 = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-activity-xblock-2', 1, 0)
        rap_assignment2.distribute(False, assignment_group_class=MockReviewAssignmentGroup)
        MockReviewAssignmentGroupCollection.load(rap_assignment2)

        '''
        There should be one assignment for test activity xblock 2 and workgroup 11
        There should be no assignments for test activity xblock 2 and workgroup 13 (workgroup doesn't exist)
        There should be no assignments for test activity xblock 3 and workgroup 12 (activity doesn't exist)
        There should be no assignments for test activity xblock 4 and workgroup 13 (both doesn't exist)
        '''
        self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(11, 'test-activity-xblock-2')), 1)
        self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(13, 'test-activity-xblock-2')), 0)
        self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(12, 'test-activity-xblock-3')), 0)
        self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(13, 'test-activity-xblock-4')), 0)

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

    def test_CreateAccessKeyForm(self):
        # valid if data is good
        form_data = {
            "client_id": 1,
            "name": "Test Key",
            "program_id": "",
            "course_id": "",
        }
        form = CreateAccessKeyForm(form_data)
        self.assertTrue(form.is_valid())

    def test_ShareAccessKeyForm(self):
        # valid if data is good
        form_data = {
            "recipients": "student1@testorg.org, student2@testorg.org",
            "message": "",
        }
        form = ShareAccessKeyForm(form_data)
        self.assertTrue(form.is_valid())


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

class ProgramTests(TestCase):

    def test_program(self):
        test_json = '{"name": "Maggie","uri": "http://localhost:56480/api/groups/39","resources": [{"uri": "http://localhost:56480/api/groups/39/users"}, {"uri": "http://localhost:56480/api/groups/39/groups"}],"data": {"display_name": "Maggie","start_date": "2014-1-1T00:00:00.00000Z","end_date": "2014-12-3T00:00:00.00000Z"},"id": 39,"group_type": "series"}'

        test_info = Program(test_json)

        self.assertEqual(test_info.name, "Maggie")
        self.assertEqual(test_info.display_name, "Maggie")
        self.assertEqual(test_info.start_date, datetime.datetime(2014,1,1))
        self.assertEqual(test_info.end_date, datetime.datetime(2014,12,3))


class MultiEmailFieldTest(TestCase):

    def test_validation(self):
        f = MultiEmailField()
        self.assertRaisesMessage(ValidationError, "'This field is required.'", f.clean, None)
        self.assertRaisesMessage(ValidationError, "'This field is required.'", f.clean, '')
        self.assertRaisesMessage(ValidationError, "'Enter a valid email address (not-an-email-adress).'",
            f.clean, 'test1@testorg.org,  not-an-email-adress, test2@testorg.org')

    def test_normalization(self):
        f = MultiEmailField()
        self.assertEqual(f.clean('test1@testorg.org, test2@testorg.org'),
            ['test1@testorg.org', 'test2@testorg.org'])
        self.assertEqual(f.clean(' test1@testorg.org  ,  ,, test2@testorg.org,,'),
            ['test1@testorg.org', 'test2@testorg.org'])
