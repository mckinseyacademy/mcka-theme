# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0002_auto_20160905_0711'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearnerDashboardTileProgress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.IntegerField()),
                ('progress', models.CharField(blank=True, max_length=1, null=True, choices=[('1', 'Not Started'), ('2', 'In Progress'), ('3', 'Complete'), ('3', 'Incomplete')])),
                ('percentage', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='learnerdashboardtile',
            name='details',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='learnerdashboardtile',
            name='download_link',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='learnerdashboardtile',
            name='end_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='learnerdashboardtile',
            name='location',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='learnerdashboardtile',
            name='publish_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='learnerdashboardtile',
            name='show_in_calendar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='learnerdashboardtile',
            name='show_in_dashboard',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='learnerdashboardtile',
            name='start_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='learnerdashboardtile',
            name='tile_type',
            field=models.CharField(max_length=1, choices=[('1', 'Article'), ('2', 'Lesson'), ('3', 'Module'), ('4', 'Course'), ('5', 'In Person Session'), ('6', 'Webinar')]),
        ),
        migrations.AddField(
            model_name='learnerdashboardtileprogress',
            name='milestone',
            field=models.ForeignKey(to='admin_apros.LearnerDashboardTile', on_delete=models.CASCADE),
        ),
    ]
