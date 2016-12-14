# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0006_learnerdashboardbranding'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learnerdashboard',
            name='client_id',
            field=models.IntegerField(null=True),
        ),
    ]
