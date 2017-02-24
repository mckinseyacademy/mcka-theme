# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0009_courserun'),
        ('accounts', '0003_auto_20170220_1209'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicRegistrationRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('company_name', models.CharField(max_length=50)),
                ('company_email', models.EmailField(max_length=254)),
                ('current_role', models.CharField(max_length=100, null=True)),
                ('current_role_other', models.CharField(max_length=60, null=True, blank=True)),
                ('mcka_user', models.BooleanField()),
                ('new_user', models.BooleanField()),
                ('course_run', models.ForeignKey(to='admin_apros.CourseRun')),
            ],
        ),
    ]
