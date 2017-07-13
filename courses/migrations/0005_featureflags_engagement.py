# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_featureflags_certificates'),
    ]

    operations = [
        migrations.AddField(
            model_name='featureflags',
            name='engagement',
            field=models.BooleanField(default=True),
        ),
    ]
