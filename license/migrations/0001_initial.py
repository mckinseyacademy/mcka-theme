# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LicenseGrant'
        db.create_table(u'license_licensegrant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('license_uuid', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('granted_id', self.gf('django.db.models.fields.IntegerField')()),
            ('grantor_id', self.gf('django.db.models.fields.IntegerField')()),
            ('grantee_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('granted_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'license', ['LicenseGrant'])


    def backwards(self, orm):
        # Deleting model 'LicenseGrant'
        db.delete_table(u'license_licensegrant')


    models = {
        u'license.licensegrant': {
            'Meta': {'object_name': 'LicenseGrant'},
            'granted_id': ('django.db.models.fields.IntegerField', [], {}),
            'granted_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'grantee_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'grantor_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license_uuid': ('django.db.models.fields.CharField', [], {'max_length': '36'})
        }
    }

    complete_apps = ['license']