# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_publicregistrationrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicregistrationrequest',
            name='company_email',
            field=models.EmailField(max_length=254),
        ),
    ]
