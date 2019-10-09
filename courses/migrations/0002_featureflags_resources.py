# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='featureflags',
            name='resources',
            field=models.BooleanField(default=True),
        ),
    ]
