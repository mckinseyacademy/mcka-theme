# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CourseCertificateStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_id', models.CharField(unique=True, max_length=200)),
                ('status', models.CharField(default=b'available', max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='UserCourseCertificate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('course_id', models.CharField(max_length=200)),
                ('email_sent', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='usercoursecertificate',
            unique_together=set([('user_id', 'course_id')]),
        ),
    ]
