# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learnerdashboard',
            name='client_id',
            field=models.IntegerField(),
        ),
    ]
