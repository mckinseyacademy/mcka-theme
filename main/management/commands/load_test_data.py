import os
import sys
import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from api_client import user_api
from api_client.api_error import ApiError

DATA_DIR = "/edx/var/edxapp/data/"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
TEST_COURSE_DIR = os.path.join(BASE_DIR, 'tests/data/test_course1')
TEST_COURSE_ID = "Arbisoft/arb001/2017_1"
UPDATE_COURSE_MSG = "As the edxapp user, run ./manage.py cms --settings=devstack import {} {}".format(
    DATA_DIR, TEST_COURSE_DIR
)


class Command(BaseCommand):
    help = "Checks whether the integration test course exists"

    def handle(self, *args, **options):
        load_msg = "Checking if the test course {} exists ...".format(TEST_COURSE_ID)
        self.stdout.write(load_msg)

        response = requests.get(settings.API_SERVER_ADDRESS + '/api/courses/v1/courses/')
        json_result = response.json()
        matching_course_list = [course for course in json_result['results'] if course['id'] == TEST_COURSE_ID]
        if not matching_course_list:
            err_msg = "Test course not found! You must import the integration test course in the CMS.\n{}".format(
                UPDATE_COURSE_MSG
            )
            self.stdout.write(err_msg)
            sys.exit(1)

        self.stdout.write("Test course exists.")

        # Check if installed version of the test course matches the current version.
        # The version is stored in the course "short_description" field.
        installed_version = matching_course_list[0]['short_description']
        with open(os.path.join(TEST_COURSE_DIR, 'about/short_description.html')) as f:
            latest_version = f.read()
        if installed_version != latest_version:
            err_msg = "Installed version is {} but latest version is {}. Please update the course.\n{}".format(
                installed_version, latest_version, UPDATE_COURSE_MSG
            )
            self.stdout.write(err_msg)
            sys.exit(1)

        # Create some users and enroll them in the test course
        user_list = ("test_course_user1",)
        for username in user_list:
            user_data = {
                "username": username,
                "first_name": username,
                "last_name": "Tester",
                "email": "{}@mckinseyacademy.com".format(username),
                "password": "PassworD12!@"
            }

            try:
                u = user_api.register_user(user_data)
                if u:
                    user_api.enroll_user_in_course(u.id, TEST_COURSE_ID)
            except ApiError as e:
                if e.code == 409:
                    self.stdout.write("User: {} already exists".format(username))
                else:
                    raise

        self.stdout.write("Done")
