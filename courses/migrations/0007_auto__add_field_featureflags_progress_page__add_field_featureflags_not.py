# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'FeatureFlags.progress_page'
        db.add_column(u'courses_featureflags', 'progress_page',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'FeatureFlags.notifications'
        db.add_column(u'courses_featureflags', 'notifications',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'FeatureFlags.progress_page'
        db.delete_column(u'courses_featureflags', 'progress_page')

        # Deleting field 'FeatureFlags.notifications'
        db.delete_column(u'courses_featureflags', 'notifications')


    models = {
        u'courses.featureflags': {
            'Meta': {'object_name': 'FeatureFlags'},
            'cohort_map': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'discussions': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'group_work': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'learner_dashboard': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notifications': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'proficiency': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'progress_page': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
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