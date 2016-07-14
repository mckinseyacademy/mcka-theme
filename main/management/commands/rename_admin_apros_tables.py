from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connections, transaction
import logging

class Command(BaseCommand):

    """
    Management command to rename admin_apros tables after Django upgrade to 1.8.13
    """
    help = """Makes database level changes to rename admin_apros app tables after upgrading Django to 1.8.13. 
        Usage: ./manage.py rename_admin_apros_tables {db_alias}
        """

    def add_arguments(self, parser):
        parser.add_argument('db_alias', type=str)

    def handle(self, *model_labels, **options):

        db_alias = options['db_alias']

        print 'TASK: Renaming tables...'

        try:
            cursor = connections[db_alias].cursor()
            cursor.execute("RENAME TABLE admin_accesskey TO admin_apros_accesskey;")
            cursor.execute("RENAME TABLE admin_batchoperationerrors TO admin_apros_batchoperationerrors;")
            cursor.execute("RENAME TABLE admin_batchoperationstatus TO admin_apros_batchoperationstatus;")
            cursor.execute("RENAME TABLE admin_brandingsettings TO admin_apros_brandingsettings;")
            cursor.execute("RENAME TABLE admin_clientcustomization TO admin_apros_clientcustomization;")
            cursor.execute("RENAME TABLE admin_clientnavlinks TO admin_apros_clientnavlinks;")
            cursor.execute("RENAME TABLE admin_companycontact TO admin_apros_companycontact;")
            cursor.execute("RENAME TABLE admin_companyinvoicingdetails TO admin_apros_companyinvoicingdetails;")
            cursor.execute("RENAME TABLE admin_dashboardadminquickfilter TO admin_apros_dashboardadminquickfilter;")
            cursor.execute("RENAME TABLE admin_emailtemplate TO admin_apros_emailtemplate;")
            cursor.execute("RENAME TABLE admin_learnerdashboard TO admin_apros_learnerdashboard;")
            cursor.execute("RENAME TABLE admin_learnerdashboarddiscovery TO admin_apros_learnerdashboarddiscovery;")
            cursor.execute("RENAME TABLE admin_learnerdashboardtile TO admin_apros_learnerdashboardtile;")
            cursor.execute("RENAME TABLE admin_tilebookmark TO admin_apros_tilebookmark;")
            cursor.execute("RENAME TABLE admin_userregistrationbatch TO admin_apros_userregistrationbatch;")
            cursor.execute("RENAME TABLE admin_userregistrationerror TO admin_apros_userregistrationerror;")
            print 'TASK: Renaming tables successful!'
        
        except:
            print "Error renaming tables!"
