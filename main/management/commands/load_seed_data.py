from django.core.management.base import BaseCommand
from api_client import course_api, user_api


class Command(BaseCommand):
    help = 'Loads seed data into the apros db and into edX via the edX API'

    def handle(self, *args, **options):
        apros_seed_msg = "Loading seed data into the Apros db..."
        edx_seed_msg = "Loading seed data via the edX API..."

        self.stdout.write(apros_seed_msg)
        self.stdout.write("Done")

        self.stdout.write(edx_seed_msg)
        # ''' Register an uber-admin user '''
        # user_data = {
        #     "username": "admin",
        #     "first_name": "Uber",
        #     "last_name": "Admin",
        #     "email": "admin@mckinseyacademy.com",
        #     "password": "password"
        # }
        # user_api.register_user(user_data)

        ''' Create roles '''
        existing_group_names = user_api.get_groups().keys()
        group_names = (
            'mcka_role_mcka_admin',
            'mcka_role_client_admin',
            'mcka_role_mcka_ta',
            'mcka_role_client_ta'
        )
        for group_name in group_names:
            import pdb;pdb.set_trace()
            if group_name not in existing_group_names:
                self.stdout.write("Creating group: %s" % group_name)
                user_api.create_group(group_name)
            else:
                self.stdout.write("Skipping %s, already exists" % group_name)

        ''' Assign uber-user to the admin role '''

        self.stdout.write("Done")
