# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0011_courserun_access_key_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='courserun',
            name='total_activations_sent',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courserun',
            name='access_key_link',
            field=models.URLField(null=True, blank=True),
        ),
    ]
