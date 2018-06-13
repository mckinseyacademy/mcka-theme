import json
import os
import csv

from django.core.management.base import BaseCommand
from django.conf import settings

from api_client import user_api
from api_client.api_error import ApiError
from mcka_apros.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Unenrolls students from courses'

    def handle(self, *args, **options):
        self.stdout.write("Unenrolling Users STARTED")

        file_path = os.path.join(BASE_DIR, 'main/fixtures/un-enroll_users.csv')

        with open(file_path) as csvfile:
            reader = csv.DictReader(csvfile)
            successful_unenrolled_count = 0
            unsuccessful_unenrolled_count = 0
            for row in reader:
                user_id = int(row['Participant_ID'])
                course_id = row['Course_ID']
                try:
                    print "Unenrolling uid: %d from course: %s" % (user_id, course_id)
                    user_api.unenroll_user_from_course(user_id, course_id)
                    successful_unenrolled_count += 1
                except ApiError as e:
                    unsuccessful_unenrolled_count +=1
                    print "User: %d not unenrolled" % (user_id)

        self.stdout.write(
            "Unenrolling Users COMPLETED with {0} out of {1} users successfully un-enrolled.".format(
                successful_unenrolled_count,
                successful_unenrolled_count + unsuccessful_unenrolled_count
            )
        )
