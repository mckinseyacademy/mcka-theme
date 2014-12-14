# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.create_table(u'active_courses', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course_id', self.gf('django.db.models.fields.CharField')(max_length=45, db_index=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('total_exercises', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))


    def backwards(self, orm):
        db.delete_table(u'active_courses')