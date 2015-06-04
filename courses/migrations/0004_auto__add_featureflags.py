# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FeatureFlags'
        db.create_table(u'courses_featureflags', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course_id', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('group_work', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('discussions', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('cohort_map', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'courses', ['FeatureFlags'])


    def backwards(self, orm):
        # Deleting model 'FeatureFlags'
        db.delete_table(u'courses_featureflags')


    models = {
        u'courses.featureflags': {
            'Meta': {'object_name': 'FeatureFlags'},
            'cohort_map': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'discussions': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'group_work': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'courses.lessonnotesitem': {
            'Meta': {'object_name': 'LessonNotesItem'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lesson_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'module_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'})
        }
    }

    complete_apps = ['courses']