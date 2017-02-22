# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0008_auto_20170201_1104'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField()),
                ('max_participants', models.IntegerField(null=True, blank=True)),
                ('opened', models.BooleanField(default=True)),
                ('mcka_course_id', models.CharField(max_length=500)),
                ('non_mcka_course_id', models.CharField(max_length=500)),
                ('mcka_email_template', models.CharField(max_length=2000)),
                ('non_mcka_email_template', models.CharField(max_length=2000)),
            ],
        ),
    ]
