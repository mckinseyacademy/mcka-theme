# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0005_auto_20161107_1046'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearnerDashboardBranding',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('background_image', models.ImageField(upload_to=b'images/learner_dashboard/branding/backgrounds/', blank=True)),
                ('logo_image', models.ImageField(upload_to=b'images/learner_dashboard/branding/logos/', blank=True)),
                ('rule_color', models.CharField(max_length=20, verbose_name=b'#000000', blank=True)),
                ('icon_color', models.CharField(max_length=20, verbose_name=b'#000000', blank=True)),
                ('discover_title_color', models.CharField(default=b'#000000', max_length=20, blank=True)),
                ('discover_author_color', models.CharField(default=b'#000000', max_length=20, blank=True)),
                ('discover_rule_color', models.CharField(default=b'#000000', max_length=20, blank=True)),
                ('background_color', models.CharField(default=b'#D3D3D3', max_length=20, blank=True)),
                ('background_style', models.CharField(blank=True, max_length=1, choices=[('1', 'Normal'), ('2', 'Tiled'), ('3', 'Stretched')])),
                ('learner_dashboard', models.ForeignKey(to='admin_apros.LearnerDashboard', on_delete=models.CASCADE)),
            ],
        ),
    ]
