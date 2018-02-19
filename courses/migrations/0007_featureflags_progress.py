# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_featureflags_discover'),
    ]

    operations = [
        migrations.AddField(
            model_name='featureflags',
            name='progress',
            field=models.BooleanField(default=True),
        ),
    ]
