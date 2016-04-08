# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'UserActivation.task_key'
        db.add_column(u'accounts_useractivation', 'task_key',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=40, db_index=True),
                      keep_default=False)

        # Adding field 'UserActivation.first_name'
        db.add_column(u'accounts_useractivation', 'first_name',
                      self.gf('django.db.models.fields.CharField')(default='N/A', max_length=40),
                      keep_default=False)

        # Adding field 'UserActivation.last_name'
        db.add_column(u'accounts_useractivation', 'last_name',
                      self.gf('django.db.models.fields.CharField')(default='N/A', max_length=40),
                      keep_default=False)

        # Adding field 'UserActivation.email'
        db.add_column(u'accounts_useractivation', 'email',
                      self.gf('django.db.models.fields.EmailField')(default='N/A', max_length=75),
                      keep_default=False)

        # Adding field 'UserActivation.company_id'
        db.add_column(u'accounts_useractivation', 'company_id',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'UserActivation.task_key'
        db.delete_column(u'accounts_useractivation', 'task_key')

        # Deleting field 'UserActivation.first_name'
        db.delete_column(u'accounts_useractivation', 'first_name')

        # Deleting field 'UserActivation.last_name'
        db.delete_column(u'accounts_useractivation', 'last_name')

        # Deleting field 'UserActivation.email'
        db.delete_column(u'accounts_useractivation', 'email')

        # Deleting field 'UserActivation.company_id'
        db.delete_column(u'accounts_useractivation', 'company_id')


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
        u'accounts.useractivation': {
            'Meta': {'object_name': 'UserActivation'},
            'activation_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40', 'db_index': 'True'}),
            'company_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "'N/A'", 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '40'}),
            'task_key': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'db_index': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'accounts.userpasswordreset': {
            'Meta': {'object_name': 'UserPasswordReset'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_requested': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'validation_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40', 'db_index': 'True'})
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

    complete_apps = ['accounts']