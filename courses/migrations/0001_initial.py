# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureFlags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_id', models.CharField(max_length=200, db_index=True)),
                ('group_work', models.BooleanField(default=True)),
                ('discussions', models.BooleanField(default=True)),
                ('cohort_map', models.BooleanField(default=True)),
                ('proficiency', models.BooleanField(default=True)),
                ('learner_dashboard', models.BooleanField(default=False)),
                ('progress_page', models.BooleanField(default=True)),
                ('notifications', models.BooleanField(default=True)),
                ('branding', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LessonNotesItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField()),
                ('user_id', models.IntegerField(null=True, db_index=True)),
                ('course_id', models.CharField(max_length=200, db_index=True)),
                ('lesson_id', models.CharField(max_length=200, db_index=True)),
                ('module_id', models.CharField(max_length=200, db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
