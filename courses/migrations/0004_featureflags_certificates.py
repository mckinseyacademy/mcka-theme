# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_featureflags_cohort_avg'),
    ]

    operations = [
        migrations.AddField(
            model_name='featureflags',
            name='certificates',
            field=models.BooleanField(default=False),
        ),
    ]
