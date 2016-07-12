# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def forward_func(apps, schema_editor):
    access_key_model = apps.get_model("admin_apros", "AccessKey")
    if access_key_model._meta.db_table == "admin_apros_accesskey":
        print "Tables are renamed."
        return
    else:
        print "Renaming tables.."

def reverse_func(apps, schema_editor):
    access_key_model = apps.get_model("admin_apros", "AccessKey")
    if access_key_model._meta.db_table == "admin_accesskey":
        print "Tables are renamed."
        return
    else:
        print "Renaming tables.."

class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
        migrations.RunSQL(
            [("RENAME TABLE admin_accesskey TO admin_apros_accesskey;")],
            [("RENAME TABLE admin_apros_accesskey TO admin_accesskey;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_batchoperationerrors TO admin_apros_batchoperationerrors;")],
            [("RENAME TABLE admin_apros_batchoperationerrors TO admin_batchoperationerrors;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_batchoperationstatus TO admin_apros_batchoperationstatus;")],
            [("RENAME TABLE admin_apros_batchoperationstatus TO admin_batchoperationstatus;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_brandingsettings TO admin_apros_brandingsettings;")],
            [("RENAME TABLE admin_apros_brandingsettings TO admin_brandingsettings;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_clientcustomization TO admin_apros_clientcustomization;")],
            [("RENAME TABLE admin_apros_clientcustomization TO admin_clientcustomization;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_clientnavlinks TO admin_apros_clientnavlinks;")],
            [("RENAME TABLE admin_apros_clientnavlinks TO admin_clientnavlinks;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_companycontact TO admin_apros_companycontact;")],
            [("RENAME TABLE admin_apros_companycontact TO admin_companycontact;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_companyinvoicingdetails TO admin_apros_companyinvoicingdetails;")],
            [("RENAME TABLE admin_apros_companyinvoicingdetails TO admin_companyinvoicingdetails;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_dashboardadminquickfilter TO admin_apros_dashboardadminquickfilter;")],
            [("RENAME TABLE admin_apros_dashboardadminquickfilter TO admin_dashboardadminquickfilter;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_emailtemplate TO admin_apros_emailtemplate;")],
            [("RENAME TABLE admin_apros_emailtemplate TO admin_emailtemplate;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_learnerdashboard TO admin_apros_learnerdashboard;")],
            [("RENAME TABLE admin_apros_learnerdashboard TO admin_learnerdashboard;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_learnerdashboarddiscovery TO admin_apros_learnerdashboarddiscovery;")],
            [("RENAME TABLE admin_apros_learnerdashboarddiscovery TO admin_learnerdashboarddiscovery;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_learnerdashboardtile TO admin_apros_learnerdashboardtile;")],
            [("RENAME TABLE admin_apros_learnerdashboardtile TO admin_learnerdashboardtile;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_tilebookmark TO admin_apros_tilebookmark;")],
            [("RENAME TABLE admin_apros_tilebookmark TO admin_tilebookmark;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_userregistrationbatch TO admin_apros_userregistrationbatch;")],
            [("RENAME TABLE admin_apros_userregistrationbatch TO admin_userregistrationbatch;")],
        ),
        migrations.RunSQL(
            [("RENAME TABLE admin_userregistrationerror TO admin_apros_userregistrationerror;")],
            [("RENAME TABLE admin_apros_userregistrationerror TO admin_userregistrationerror;")],
        ),
    ]
