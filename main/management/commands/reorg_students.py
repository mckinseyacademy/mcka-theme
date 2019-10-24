import json
import os

from django.core.management.base import BaseCommand, CommandError

from api_client import organization_api
from api_client.api_error import ApiError


class Command(BaseCommand):
    help = 'Reorganizes students to/from orgs'

    def handle(self, *args, **options):
        unenroll_msg = "Reorganizing students..."
        self.stdout.write(unenroll_msg)
        if len(args) == 0:
            raise CommandError("A file path must be specified")
        filename = args[0]
        if not os.path.isfile(filename):
            raise CommandError("File does not exist at the specified path.")

        with open(filename) as json_file:
            org_list = json.load(json_file)
            for org in org_list:
                for uid in org["add"]:
                    try:
                        print("Adding uid: %d to org: %d" % (uid, org["org_id"]))
                        organization_api.add_user_to_organization(org["org_id"], uid)
                    except ApiError:
                        print("User: %d not added" % (uid))

                for uid in org["remove"]:
                    try:
                        print("Removing uid: %d from org: %d" % (uid, org["org_id"]))
                    except ApiError:
                        print("User: %d not removed" % (uid))

        self.stdout.write("Done")
