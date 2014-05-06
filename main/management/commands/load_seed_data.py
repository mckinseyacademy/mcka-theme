from django.core.management.base import BaseCommand
from urllib2 import HTTPError
from api_client import course_api, group_api, user_api


class Command(BaseCommand):
    help = 'Loads seed data into the apros db and into edX via the edX API'

    def handle(self, *args, **options):
        apros_seed_msg = "Loading seed data into the Apros db..."
        edx_seed_msg = "Loading seed data via the edX API..."

        self.stdout.write(apros_seed_msg)
        # Load Apros seed data here
        self.stdout.write("Done")

        self.stdout.write(edx_seed_msg)
        
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

        ''' Register an uber-admin user '''
        u = None
        user_data = {
            "username": "admin111",
            "first_name": "Uber",
            "last_name": "Admin",
            "email": "admin111@mckinseyacademy.com",
            "password": "password"
        }
        try:
            self.stdout.write("Registering an admin user")
            u = user_api.register_user(user_data)
            import pdb;pdb.set_trace()
        except HTTPError as e:
            if e.code == 409:
                self.stdout.write("User already exists")
            else: 
                raise

        ''' Assign uber-user to the admin role '''
        self.stdout.write("Registering an uber user")
        group_api.add_user_to_group()

        self.stdout.write("Done")
