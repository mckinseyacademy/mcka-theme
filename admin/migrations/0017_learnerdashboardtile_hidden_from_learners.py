# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-06 08:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0016_auto_20181009_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='learnerdashboardtile',
            name='hidden_from_learners',
            field=models.BooleanField(default=False),
        ),
    ]
