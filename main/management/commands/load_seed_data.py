from django.core.management.base import BaseCommand
from django.conf import settings

from api_client import group_api, user_api
from api_client.api_error import ApiError
from api_client.organization_models import Organization
from lib.authorization import permission_groups_map


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
        group_names = [group_api.PERMISSION_GROUPS[key] for key in list(group_api.PERMISSION_GROUPS.keys())]

        for group_name in group_names:
            if group_name not in existing_group_names:
                self.stdout.write("Creating group: %s" % group_name)
                group_api.create_group(group_name, group_type)
            else:
                self.stdout.write("Skipping %s, already exists" % group_name)

        ''' Register McK and TA users '''
        user_suffix = '_user'
        user_list = (
            ('mcka_admin%s' % user_suffix, group_api.PERMISSION_GROUPS.MCKA_ADMIN),
            ('mcka_subadmin%s' % user_suffix, group_api.PERMISSION_GROUPS.MCKA_SUBADMIN),
            ('mcka_ta%s' % user_suffix, group_api.PERMISSION_GROUPS.MCKA_TA),
            ('mcka_observer%s' % user_suffix, group_api.PERMISSION_GROUPS.MCKA_OBSERVER),
            ('client_admin%s' % user_suffix, group_api.PERMISSION_GROUPS.CLIENT_ADMIN),
            ('client_subadmin%s' % user_suffix, group_api.PERMISSION_GROUPS.CLIENT_SUBADMIN),
            ('client_ta%s' % user_suffix, group_api.PERMISSION_GROUPS.CLIENT_TA),
            ('client_observer%s' % user_suffix, group_api.PERMISSION_GROUPS.CLIENT_OBSERVER),
        )
        for user_tuple in user_list:
            user_data = {
                "username": user_tuple[0],
                "first_name": user_tuple[0],
                "last_name": "Tester",
                "email": "%s@mckinseyacademy.com" % user_tuple[0],
                "password": "PassworD12!@"
            }
            try:
                self.stdout.write("Registering user: %s in the role: %s" % (user_tuple[0], user_tuple[1]))
                u = user_api.register_user(user_data)
                if u:
                    group_api.add_users_to_group([u.id], permission_groups_map()[user_tuple[1]])
            except ApiError as e:
                if e.code == 409:
                    self.stdout.write("User: %s already exists" % user_tuple[0])
                else:
                    raise

        ''' Administrative company '''
        admin_company = None
        for org in Organization.list():
            if org.name == settings.ADMINISTRATIVE_COMPANY:
                self.stdout.write("Administrative company %s already exists" % settings.ADMINISTRATIVE_COMPANY)
                admin_company = Organization.fetch(org.id)
                break

        if admin_company is None:
            self.stdout.write("Creating administrative company %s" % settings.ADMINISTRATIVE_COMPANY)
            company_data = {
                "display_name": "McKinsey and Company",
                "contact_name": "McKinsey and Company",
                "contact_email": "company@mckinseyacademy.com",
                "contact_phone": "",
            }
            admin_company = Organization.create(settings.ADMINISTRATIVE_COMPANY, company_data)

        for user_tuple in user_list:
            if (user_tuple[0].startswith('mcka')):
                users = user_api.get_users(username=user_tuple[0])
                if users:
                    self.stdout.write("Adding %s to %s" % (user_tuple[0], settings.ADMINISTRATIVE_COMPANY))
                    admin_company.add_user(users[0].id)

        self.stdout.write("Done")
