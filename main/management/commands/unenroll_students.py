import json
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from api_client import user_api
from api_client.api_error import ApiError

class Command(BaseCommand):
    help = 'Unenrolls students from courses'

    def handle(self, *args, **options):
        unenroll_msg = "Unenrolling students..."
        self.stdout.write(unenroll_msg)
        if len(args) == 0:
            raise CommandError("A file path must be specified")
        filename = args[0]
        if not os.path.isfile(filename):
            raise CommandError("File does not exist at the specified path.")

        with open(filename) as json_file:
            course_list = json.load(json_file)
            for course in course_list:

                for uid in course["users"]:
                    try:
                        print "Unenrolling uid: %d from course: %s" % (uid, course["id"])
                        user_api.unenroll_user_from_course(uid, course["id"])
                    except ApiError as e:
                        print "User: %d not unenrolled" % (uid)

        self.stdout.write("Done")
