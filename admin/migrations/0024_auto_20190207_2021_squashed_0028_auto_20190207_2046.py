# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-08 01:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [(b'admin_apros', '0024_auto_20190207_2021'), (b'admin_apros', '0025_auto_20190207_2031'), (b'admin_apros', '0026_admintask_problem_location'), (b'admin_apros', '0027_auto_20190207_2039'), (b'admin_apros', '0028_auto_20190207_2046')]

    dependencies = [
        ('admin_apros', '0023_clientcustomization_new_ui_enabled'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(max_length=255)),
                ('parameters', models.TextField(blank=True, null=True)),
                ('task_type', models.CharField(max_length=512)),
                ('output', models.TextField(blank=True, null=True)),
                ('status', models.CharField(default=b'PROGRESS', max_length=215)),
            ],
        ),
        migrations.AddIndex(
            model_name='admintask',
            index=models.Index(fields=[b'task_id'], name='admin_apros_task_id_887e27_idx'),
        ),
        migrations.AddIndex(
            model_name='admintask',
            index=models.Index(fields=[b'task_id', b'task_type'], name='admin_apros_task_id_7a879c_idx'),
        ),
        migrations.AddField(
            model_name='admintask',
            name='course_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='admintask',
            name='parameters',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddIndex(
            model_name='admintask',
            index=models.Index(fields=[b'course_id'], name='admin_apros_course__67e28d_idx'),
        ),
        migrations.AddField(
            model_name='admintask',
            name='problem_location',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.RemoveIndex(
            model_name='admintask',
            name='admin_apros_task_id_7a879c_idx',
        ),
        migrations.AddIndex(
            model_name='admintask',
            index=models.Index(fields=[b'task_id', b'course_id', b'task_type'], name='admin_apros_task_id_49ed0a_idx'),
        ),
        migrations.RemoveIndex(
            model_name='admintask',
            name='admin_apros_task_id_49ed0a_idx',
        ),
    ]
