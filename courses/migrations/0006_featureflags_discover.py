# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_featureflags_engagement'),
    ]

    operations = [
        migrations.AddField(
            model_name='featureflags',
            name='discover',
            field=models.BooleanField(default=True),
        ),
    ]
