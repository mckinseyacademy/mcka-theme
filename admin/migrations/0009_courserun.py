# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0008_auto_20170201_1104'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(unique=True)),
                ('max_participants', models.IntegerField(null=True, blank=True)),
                ('total_participants', models.IntegerField(default=0, null=True, blank=True)),
                ('is_open', models.BooleanField(default=True)),
                ('course_id', models.CharField(max_length=500)),
                ('course_id_sso', models.CharField(max_length=500, null=True, blank=True)),
                ('email_template_new', models.CharField(max_length=2000)),
                ('email_template_existing', models.CharField(max_length=2000)),
                ('email_template_mcka', models.CharField(max_length=2000)),
                ('email_template_closed', models.CharField(max_length=2000)),
            ],
        ),
    ]
