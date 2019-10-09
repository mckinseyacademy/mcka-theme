from django.core.management.base import BaseCommand
from django.db import connections


def get_table_names():
    """
    Returns list of table names for admin_apros app
    """
    return [
        'accesskey',
        'batchoperationerrors',
        'batchoperationstatus',
        'brandingsettings',
        'clientcustomization',
        'clientnavlinks',
        'companycontact',
        'companyinvoicingdetails',
        'dashboardadminquickfilter',
        'emailtemplate',
        'learnerdashboard',
        'learnerdashboarddiscovery',
        'learnerdashboardtile',
        'tilebookmark',
        'userregistrationbatch',
        'userregistrationerror',
    ]


class Command(BaseCommand):
    """
    Management command to revert rename admin_apros tables before Django downgrade
    """
    help = """Makes database level changes to revert rename admin_apros app tables
        Usage: ./manage.py revert_admin_apros_tables {db_alias}
        """

    old_app = 'admin'
    new_app = 'admin_apros'

    def add_arguments(self, parser):
        parser.add_argument('db_alias', type=str)

    def handle(self, *model_labels, **options):

        warnings = 0
        db_alias = options['db_alias']

        cursor = connections[db_alias].cursor()

        for table_name in get_table_names():

            """Rename the admin_apros tables"""
            try:
                sql_tables = 'RENAME TABLE %s_%s TO %s_%s;' % (self.new_app, table_name, self.old_app, table_name)
                cursor.execute(sql_tables)
            except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
                print("Warning: Problem renaming table: " + table_name)
                warnings += 1

            """Rename the app_labels in django_content_type"""
            try:
                sql_models = 'UPDATE django_content_type SET app_label = "%s" ' \
                             'WHERE (model = "%s" AND app_label = "%s")' % (self.old_app, table_name, self.new_app)
                cursor.execute(sql_models)
            except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
                print("Warning: Problem renaming django_content_type table where model = " + table_name)
                warnings += 1

        if warnings == 0:
            print("Tables rename sucess!")
        else:
            print("There was " + str(warnings) + " warnings")
