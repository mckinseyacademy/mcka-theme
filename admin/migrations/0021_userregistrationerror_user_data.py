# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-22 18:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0020_auto_20181122_0612'),
    ]

    operations = [
        migrations.AddField(
            model_name='userregistrationerror',
            name='user_data',
            field=models.TextField(blank=True, null=True),
        ),
    ]