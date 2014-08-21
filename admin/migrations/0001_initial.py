# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserRegistrationBatch'
        db.create_table(u'admin_userregistration_batch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task_key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40, db_index=True)),
            ('attempted', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('failed', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('succeded', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('time_requested', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'admin', ['UserRegistrationBatch'])

        db.create_table(u'admin_userregistration_error', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task_key', self.gf('django.db.models.fields.CharField')(unique=False, max_length=40, db_index=True)),
            ('attempted', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal(u'admin', ['UserRegistrationError'])


    def backwards(self, orm):
        # Deleting model 'UserRegistrationBatch'
        db.delete_table(u'admin_userregistration_batch')
        db.delete_table(u'admin_userregistration_error')

    models = {
        u'admin.userregistration_batch': {
            'Meta': {'object_name': 'UserRegistrationBatch'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40', 'db_index': 'True'}),
            'time_requested': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'attempted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'failed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'succeded': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },

        u'admin.userregistration_error': {
            'Meta': {'object_name': 'UserRegistrationError'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task_key': ('django.db.models.fields.CharField', [], {'unique': 'False', 'max_length': '40', 'db_index': 'True'}),
            'error': ('django.db.models.fields.TextField', [], {'default': ''})
        },
    }

    complete_apps = ['admin']
