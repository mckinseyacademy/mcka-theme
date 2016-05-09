# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'LearnerDashboardResource'
        db.delete_table(u'admin_learnerdashboardresource')

        # Adding model 'CompanyContact'
        db.create_table(u'admin_companycontact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('contact_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'admin', ['CompanyContact'])

        # Adding unique constraint on 'CompanyContact', fields ['company_id', 'contact_type']
        db.create_unique(u'admin_companycontact', ['company_id', 'contact_type'])

        # Adding model 'CompanyInvoicingDetails'
        db.create_table(u'admin_companyinvoicingdetails', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(unique=True, db_index=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('address1', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('address2', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('po', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'admin', ['CompanyInvoicingDetails'])

        # Adding field 'LearnerDashboard.title_color'
        db.add_column(u'admin_learnerdashboard', 'title_color',
                      self.gf('django.db.models.fields.CharField')(default='#FFFFFF', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'LearnerDashboard.description_color'
        db.add_column(u'admin_learnerdashboard', 'description_color',
                      self.gf('django.db.models.fields.CharField')(default='#FFFFFF', max_length=20, blank=True),
                      keep_default=False)


        # Changing field 'LearnerDashboardDiscovery.title'
        db.alter_column(u'admin_learnerdashboarddiscovery', 'title', self.gf('django.db.models.fields.CharField')(max_length=5000, null=True))

        # Changing field 'LearnerDashboardDiscovery.author'
        db.alter_column(u'admin_learnerdashboarddiscovery', 'author', self.gf('django.db.models.fields.CharField')(max_length=5000, null=True))

        # Changing field 'LearnerDashboardDiscovery.link'
        db.alter_column(u'admin_learnerdashboarddiscovery', 'link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True))
        # Deleting field 'BrandingSettings.discover_navigation_color'
        db.delete_column(u'admin_brandingsettings', 'discover_navigation_color')

        # Deleting field 'BrandingSettings.navigation_color'
        db.delete_column(u'admin_brandingsettings', 'navigation_color')

        # Deleting field 'BrandingSettings.title_color'
        db.delete_column(u'admin_brandingsettings', 'title_color')

        # Deleting field 'BrandingSettings.discover_text_color'
        db.delete_column(u'admin_brandingsettings', 'discover_text_color')

        # Adding field 'BrandingSettings.rule_color'
        db.add_column(u'admin_brandingsettings', 'rule_color',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'BrandingSettings.discover_title_color'
        db.add_column(u'admin_brandingsettings', 'discover_title_color',
                      self.gf('django.db.models.fields.CharField')(default='#000000', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'BrandingSettings.discover_author_color'
        db.add_column(u'admin_brandingsettings', 'discover_author_color',
                      self.gf('django.db.models.fields.CharField')(default='#000000', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'BrandingSettings.discover_rule_color'
        db.add_column(u'admin_brandingsettings', 'discover_rule_color',
                      self.gf('django.db.models.fields.CharField')(default='#000000', max_length=20, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Removing unique constraint on 'CompanyContact', fields ['company_id', 'contact_type']
        db.delete_unique(u'admin_companycontact', ['company_id', 'contact_type'])

        # Adding model 'LearnerDashboardResource'
        db.create_table(u'admin_learnerdashboardresource', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('learner_dashboard', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admin.LearnerDashboard'])),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'admin', ['LearnerDashboardResource'])

        # Deleting model 'CompanyContact'
        db.delete_table(u'admin_companycontact')

        # Deleting model 'CompanyInvoicingDetails'
        db.delete_table(u'admin_companyinvoicingdetails')

        # Deleting field 'LearnerDashboard.title_color'
        db.delete_column(u'admin_learnerdashboard', 'title_color')

        # Deleting field 'LearnerDashboard.description_color'
        db.delete_column(u'admin_learnerdashboard', 'description_color')


        # User chose to not deal with backwards NULL issues for 'LearnerDashboardDiscovery.title'
        raise RuntimeError("Cannot reverse this migration. 'LearnerDashboardDiscovery.title' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'LearnerDashboardDiscovery.title'
        db.alter_column(u'admin_learnerdashboarddiscovery', 'title', self.gf('django.db.models.fields.CharField')(max_length=5000))

        # Changing field 'LearnerDashboardDiscovery.author'
        db.alter_column(u'admin_learnerdashboarddiscovery', 'author', self.gf('django.db.models.fields.CharField')(default='', max_length=5000))

        # User chose to not deal with backwards NULL issues for 'LearnerDashboardDiscovery.link'
        raise RuntimeError("Cannot reverse this migration. 'LearnerDashboardDiscovery.link' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'LearnerDashboardDiscovery.link'
        db.alter_column(u'admin_learnerdashboarddiscovery', 'link', self.gf('django.db.models.fields.URLField')(max_length=200))
        # Adding field 'BrandingSettings.discover_navigation_color'
        db.add_column(u'admin_brandingsettings', 'discover_navigation_color',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'BrandingSettings.navigation_color'
        db.add_column(u'admin_brandingsettings', 'navigation_color',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'BrandingSettings.title_color'
        db.add_column(u'admin_brandingsettings', 'title_color',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'BrandingSettings.discover_text_color'
        db.add_column(u'admin_brandingsettings', 'discover_text_color',
                      self.gf('django.db.models.fields.CharField')(default='#FFFFFF', max_length=20, blank=True),
                      keep_default=False)

        # Deleting field 'BrandingSettings.rule_color'
        db.delete_column(u'admin_brandingsettings', 'rule_color')

        # Deleting field 'BrandingSettings.discover_title_color'
        db.delete_column(u'admin_brandingsettings', 'discover_title_color')

        # Deleting field 'BrandingSettings.discover_author_color'
        db.delete_column(u'admin_brandingsettings', 'discover_author_color')

        # Deleting field 'BrandingSettings.discover_rule_color'
        db.delete_column(u'admin_brandingsettings', 'discover_rule_color')


    models = {
        u'accounts.remoteuser': {
            'Meta': {'object_name': 'RemoteUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'session_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'admin.accesskey': {
            'Meta': {'object_name': 'AccessKey'},
            'client_id': ('django.db.models.fields.IntegerField', [], {}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'program_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'admin.batchoperationerrors': {
            'Meta': {'object_name': 'BatchOperationErrors'},
            'error': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'admin.batchoperationstatus': {
            'Meta': {'object_name': 'BatchOperationStatus'},
            'attempted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'failed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'succeded': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'task_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40', 'db_index': 'True'}),
            'time_requested': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'admin.brandingsettings': {
            'Meta': {'object_name': 'BrandingSettings'},
            'background_color': ('django.db.models.fields.CharField', [], {'default': "'#D3D3D3'", 'max_length': '20', 'blank': 'True'}),
            'background_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'background_style': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'client_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'discover_author_color': ('django.db.models.fields.CharField', [], {'default': "'#000000'", 'max_length': '20', 'blank': 'True'}),
            'discover_rule_color': ('django.db.models.fields.CharField', [], {'default': "'#000000'", 'max_length': '20', 'blank': 'True'}),
            'discover_title_color': ('django.db.models.fields.CharField', [], {'default': "'#000000'", 'max_length': '20', 'blank': 'True'}),
            'icon_color': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'rule_color': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'admin.clientcustomization': {
            'Meta': {'object_name': 'ClientCustomization'},
            'client_background': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'client_background_css': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'client_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'client_logo': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'hex_background_bar': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'hex_course_title': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'hex_navigation_icons': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'hex_notification': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'hex_notification_text': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'hex_page_background': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'hex_program_name': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity_provider': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'admin.clientnavlinks': {
            'Meta': {'unique_together': "(['client_id', 'link_name'],)", 'object_name': 'ClientNavLinks'},
            'client_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'link_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'link_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'admin.companycontact': {
            'Meta': {'unique_together': "(['company_id', 'contact_type'],)", 'object_name': 'CompanyContact'},
            'company_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'contact_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'admin.companyinvoicingdetails': {
            'Meta': {'object_name': 'CompanyInvoicingDetails'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'company_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'po': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'admin.dashboardadminquickfilter': {
            'Meta': {'ordering': "('date_created',)", 'object_name': 'DashboardAdminQuickFilter'},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'group_work_project_id': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'program_id': ('django.db.models.fields.IntegerField', [], {}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        u'admin.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            'body': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'admin.learnerdashboard': {
            'Meta': {'object_name': 'LearnerDashboard'},
            'client_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'blank': 'True'}),
            'description_color': ('django.db.models.fields.CharField', [], {'default': "'#FFFFFF'", 'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'title_color': ('django.db.models.fields.CharField', [], {'default': "'#FFFFFF'", 'max_length': '20', 'blank': 'True'})
        },
        u'admin.learnerdashboarddiscovery': {
            'Meta': {'object_name': 'LearnerDashboardDiscovery'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'learner_dashboard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.LearnerDashboard']"}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'null': 'True', 'blank': 'True'})
        },
        u'admin.learnerdashboardtile': {
            'Meta': {'object_name': 'LearnerDashboardTile'},
            'background_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'label_color': ('django.db.models.fields.CharField', [], {'default': "'#000000'", 'max_length': '20', 'blank': 'True'}),
            'learner_dashboard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.LearnerDashboard']"}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'note_color': ('django.db.models.fields.CharField', [], {'default': "'#868685'", 'max_length': '20', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'tile_background_color': ('django.db.models.fields.CharField', [], {'default': "'#FFFFFF'", 'max_length': '20', 'blank': 'True'}),
            'tile_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'title_color': ('django.db.models.fields.CharField', [], {'default': "'#3384CA'", 'max_length': '20', 'blank': 'True'})
        },
        u'admin.logentry': {
            'Meta': {'ordering': "(u'-action_time',)", 'object_name': 'LogEntry', 'db_table': "u'django_admin_log'"},
            'action_flag': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'action_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'change_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'object_repr': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.RemoteUser']"})
        },
        u'admin.userregistrationbatch': {
            'Meta': {'object_name': 'UserRegistrationBatch'},
            'attempted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'failed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'succeded': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'task_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40', 'db_index': 'True'}),
            'time_requested': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'admin.userregistrationerror': {
            'Meta': {'object_name': 'UserRegistrationError'},
            'error': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['admin']