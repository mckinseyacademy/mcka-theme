from django.core.management.base import BaseCommand

from api_client import group_api
from api_client.api_error import ApiError
from license.models import LicenseGrant


class Command(BaseCommand):
    help = 'Updates the program ("series") groups to match the license information in the Apros database'

    def handle(self, *args, **options):
        all_licenses = LicenseGrant.objects.all()
        for license in all_licenses:
            if license.grantee_id is not None:
                try:
                    group_api.add_users_to_group([license.grantee_id], license.granted_id)
                except ApiError as e:
                    # Ignore 409 errors, because they indicate a user already added
                    if e.code != 409:
                        print("Failed adding user {} to group {} - code {}".format(
                            license.grantee_id,
                            license.granted_id,
                            e.code,
                        ))
