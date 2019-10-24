# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_featureflags_progress'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseMetaData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_id', models.CharField(unique=True, max_length=200, db_index=True)),
                ('lesson_label', models.CharField(max_length=20, blank=True)),
                ('module_label', models.CharField(max_length=20, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
