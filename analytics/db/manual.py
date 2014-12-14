from django.db import connections
from django.conf import settings
from django.db import models
from south.db import db

db.create_table(u'active_courses', (
	(u'id', models.AutoField(primary_key=True)),
    ('course_id', models.fields.CharField(max_length=45, db_index=True)),
    ('is_active', models.fields.BooleanField(default=False)),
    ('total_exercises', models.fields.IntegerField(default=0)),
))