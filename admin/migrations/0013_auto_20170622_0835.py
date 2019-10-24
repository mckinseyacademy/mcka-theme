# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0012_auto_20170323_0626'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientcustomization',
            name='global_client_logo',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='clientcustomization',
            name='hex_background_main_navigation',
            field=models.CharField(max_length=7, blank=True),
        ),
    ]
