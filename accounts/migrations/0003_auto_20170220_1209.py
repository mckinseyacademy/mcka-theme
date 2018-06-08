# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    # Note: We are making this migration blank as it is somehow handled badly in the past
    # We have included migration 0006_auto_20180605_2114 to fix this issue
    dependencies = [
        ('accounts', '0002_auto_20160705_1123'),
    ]

    operations = []
