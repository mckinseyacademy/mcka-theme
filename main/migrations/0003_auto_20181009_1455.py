# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-09 14:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20160607_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curatedcontentitem',
            name='title',
            field=models.CharField(blank=True, default=b'', max_length=255),
        ),
        migrations.AlterField(
            model_name='curatedcontentitem',
            name='url',
            field=models.URLField(blank=True, default=b''),
        ),
    ]
