# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0003_auto_20160905_0823'),
    ]

    operations = [
        migrations.AddField(
            model_name='learnerdashboardtile',
            name='fa_icon',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AddField(
            model_name='learnerdashboardtile',
            name='row',
            field=models.CharField(blank=True, max_length=1, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]),
        ),
    ]
