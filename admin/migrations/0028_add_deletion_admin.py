# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-10 17:30


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0027_clientcustomization_new_ui_enabled_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletionAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=255, unique=True)),
            ],
        ),
    ]