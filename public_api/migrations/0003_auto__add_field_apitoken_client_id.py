# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ApiToken.client_id'
        db.add_column(u'public_api_apitoken', 'client_id',
                      self.gf('django.db.models.fields.IntegerField')(default=0, unique=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ApiToken.client_id'
        db.delete_column(u'public_api_apitoken', 'client_id')


    models = {
        u'public_api.apitoken': {
            'Meta': {'object_name': 'ApiToken'},
            'client_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'unique': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['public_api']