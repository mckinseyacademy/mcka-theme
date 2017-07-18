# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0013_auto_20170622_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyinvoicingdetails',
            name='identity_provider',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
