# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'LearnerDashboardTile.order'
        db.delete_column(u'admin_learnerdashboardtile', 'order')

        # Adding field 'LearnerDashboardTile.position'
        db.add_column(u'admin_learnerdashboardtile', 'position',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Deleting field 'LearnerDashboardDiscovery.order'
        db.delete_column(u'admin_learnerdashboarddiscovery', 'order')

        # Adding field 'LearnerDashboardDiscovery.position'
        db.add_column(u'admin_learnerdashboarddiscovery', 'position',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'LearnerDashboardTile.order'
        db.add_column(u'admin_learnerdashboardtile', 'order',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Deleting field 'LearnerDashboardTile.position'
        db.delete_column(u'admin_learnerdashboardtile', 'position')

        # Adding field 'LearnerDashboardDiscovery.order'
        db.add_column(u'admin_learnerdashboarddiscovery', 'order',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Deleting field 'LearnerDashboardDiscovery.position'
        db.delete_column(u'admin_learnerdashboarddiscovery', 'position')


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
            'background_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'background_tiled': ('django.db.models.fields.BooleanField', [], {}),
            'client_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'navigation_colors': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'text_colors': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
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
        u'admin.learnerdashboard': {
            'Meta': {'object_name': 'LearnerDashboard'},
            'client_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'})
        },
        u'admin.learnerdashboarddiscovery': {
            'Meta': {'object_name': 'LearnerDashboardDiscovery'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'learner_dashboard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.LearnerDashboard']"}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'admin.learnerdashboardresource': {
            'Meta': {'object_name': 'LearnerDashboardResource'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'learner_dashboard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.LearnerDashboard']"}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'admin.learnerdashboardtile': {
            'Meta': {'object_name': 'LearnerDashboardTile'},
            'background_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'learner_dashboard': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.LearnerDashboard']"}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'tile_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
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