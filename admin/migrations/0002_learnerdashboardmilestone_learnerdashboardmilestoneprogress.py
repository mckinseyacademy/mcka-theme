# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearnerDashboardMilestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=20, blank=True)),
                ('title', models.CharField(max_length=5000)),
                ('location', models.CharField(max_length=250, blank=True)),
                ('download_link', models.URLField(null=True, blank=True)),
                ('details_link', models.URLField(null=True, blank=True)),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('active', models.BooleanField(default=False)),
                ('milestone_type', models.CharField(max_length=1, choices=[('1', 'In Person Session'), ('2', 'Webinar'), ('3', 'Digital Content')])),
                ('digital_content_type', models.CharField(blank=True, max_length=1, choices=[('1', 'Prework'), ('2', 'Single Module'), ('3', 'External Content')])),
                ('learner_dashboard', models.ForeignKey(to='admin_apros.LearnerDashboard')),
            ],
        ),
        migrations.CreateModel(
            name='LearnerDashboardMilestoneProgress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.IntegerField(unique=True)),
                ('progress', models.CharField(max_length=1, choices=[('1', 'Not Started'), ('2', 'In Progress'), ('3', 'Complete'), ('3', 'Incomplete')])),
                ('learner_dashboard', models.ForeignKey(to='admin_apros.LearnerDashboard')),
                ('milestone', models.ForeignKey(to='admin_apros.LearnerDashboardMilestone')),
            ],
        ),
    ]
