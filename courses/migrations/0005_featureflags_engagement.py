# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_featureflags_certificates'),
    ]

    operations = [
        migrations.AddField(
            model_name='featureflags',
            name='engagement',
            field=models.BooleanField(default=True),
        ),
    ]
