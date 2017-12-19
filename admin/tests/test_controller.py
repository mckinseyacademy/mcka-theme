import os

from django.test import TestCase
from django.test.client import RequestFactory

import admin.controller as controller
from admin.tests.utils import BASE_DIR


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

