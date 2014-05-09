from django.core.management.base import BaseCommand
from urllib2 import HTTPError
from lib.authorization import permission_groups_map
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
        group_names = [group_api.PERMISSION_GROUPS[key] for key in group_api.PERMISSION_GROUPS.keys()]

        for group_name in group_names:
            if group_name not in existing_group_names:
                self.stdout.write("Creating group: %s" % group_name)
                # TODO: the group_data param should not be required but there is a 
                # db constraint as of 4/29/2014. Remove the param when this is fixed in 
                # edx-platform
                group_api.create_group(group_name, group_type, group_data='placeholder')
            else:
                self.stdout.write("Skipping %s, already exists" % group_name)

        ''' Register admin, sub-admin and TA users '''
        user_suffix = '_user'
        user_list = (
            ('admin%s' % user_suffix, group_api.PERMISSION_GROUPS.MCKA_ADMIN),
            ('subadmin%s' % user_suffix, group_api.PERMISSION_GROUPS.MCKA_SUBADMIN),
            ('ta%s' % user_suffix, group_api.PERMISSION_GROUPS.MCKA_TA)
        )
        for user_tuple in user_list:
            user_data = {
                "username": user_tuple[0],
                "first_name": "Uber",
                "last_name": "Admin",
                "email": "%s@mckinseyacademy.com" % user_tuple[0],
                "password": "PassworD12!@"
            }
            try:
                self.stdout.write("Registering user: %s in the role: %s" % (user_tuple[0], user_tuple[1]))
                u = user_api.register_user(user_data)
                group_api.add_user_to_group(u.id, permission_groups_map()[user_tuple[1]])
            except HTTPError as e:
                if e.code == 409:
                    self.stdout.write("User: %s already exists" % user_tuple[0])
                else: 
                    raise

        self.stdout.write("Done")
