# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CuratedContentItem.sequence'
        db.add_column('curated_content_item', 'sequence',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CuratedContentItem.sequence'
        db.delete_column('curated_content_item', 'sequence')


    models = {
        u'main.curatedcontentitem': {
            'Meta': {'object_name': 'CuratedContentItem', 'db_table': "'curated_content_item'"},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'byline': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'txt'", 'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['main']