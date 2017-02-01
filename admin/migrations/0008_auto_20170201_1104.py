# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0007_auto_20161208_0838'),
    ]

    operations = [
        migrations.AddField(
            model_name='brandingsettings',
            name='top_bar_color',
            field=models.CharField(default=b'#ffffff', max_length=20, blank=True),
        ),
        migrations.AddField(
            model_name='learnerdashboardbranding',
            name='top_bar_color',
            field=models.CharField(default=b'#ffffff', max_length=20, blank=True),
        ),
    ]
