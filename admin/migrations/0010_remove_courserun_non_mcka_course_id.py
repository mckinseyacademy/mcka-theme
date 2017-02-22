# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0009_courserun'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='courserun',
            name='non_mcka_course_id',
        ),
    ]
