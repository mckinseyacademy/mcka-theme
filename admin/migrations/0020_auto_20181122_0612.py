# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-22 11:12


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0019_auto_20181108_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userregistrationerror',
            name='user_email',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
