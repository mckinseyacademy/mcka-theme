# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_featureflags_resources'),
    ]

    operations = [
        migrations.AddField(
            model_name='featureflags',
            name='cohort_avg',
            field=models.BooleanField(default=True),
        ),
    ]
