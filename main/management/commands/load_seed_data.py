from django.core.management.base import BaseCommand
from api_client import course_api, group_api, user_api


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
        group_type = 'permission'
        existing_groups = group_api.get_groups_of_type(group_type)
        existing_group_names = [existing_group.name for existing_group in existing_groups]
        group_names = (
            'mcka_role_mcka_admin',
            'mcka_role_mcka_subadmin',
            
            'mcka_role_client_admin',
            'mcka_role_client_subadmin',
            
            'mcka_role_mcka_ta',
            'mcka_role_client_ta'
        )
        
        for group_name in group_names:
            if group_name not in existing_group_names:
                self.stdout.write("Creating group: %s" % group_name)
                # TODO: the group_data param should not be required but there is a 
                # db constraint as of 4/29/2014. Remove the param when this is fixed in 
                # edx-platform
                group_api.create_group(group_name, group_type, group_data='placeholder')
            else:
                self.stdout.write("Skipping %s, already exists" % group_name)

        ''' Assign uber-user to the admin role '''

        self.stdout.write("Done")
