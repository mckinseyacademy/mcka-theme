# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0004_auto_20161007_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='learnerdashboardtile',
            name='track_progress',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='learnerdashboardtile',
            name='tile_type',
            field=models.CharField(max_length=1, choices=[('1', 'Article'), ('2', 'Lesson'), ('3', 'Module'), ('4', 'Course'), ('5', 'In Person Session'), ('6', 'Webinar'), ('7', 'Group work')]),
        ),
    ]
