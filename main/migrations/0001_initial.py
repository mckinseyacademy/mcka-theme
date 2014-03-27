# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CuratedContentItem'
        db.create_table(u'main_curatedcontentitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('body', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True)),
            ('byline', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('image_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.CharField')(default='txt', max_length=3)),
        ))
        db.send_create_signal(u'main', ['CuratedContentItem'])


    def backwards(self, orm):
        # Deleting model 'CuratedContentItem'
        db.delete_table(u'main_curatedcontentitem')


    models = {
        u'main.curatedcontentitem': {
            'Meta': {'object_name': 'CuratedContentItem'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'byline': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'txt'", 'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['main']