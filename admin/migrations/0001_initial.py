# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=50)),
                ('client_id', models.IntegerField()),
                ('course_id', models.CharField(max_length=200, blank=True)),
                ('program_id', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=200)),
                ('disabled', models.BooleanField(default=False)),
                ('expiration_date', models.DateTimeField(null=True, blank=True)),
                ('user_count', models.IntegerField(default=0, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BatchOperationErrors',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_key', models.CharField(max_length=40, db_index=True)),
                ('error', models.TextField(default=b'')),
                ('user_id', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BatchOperationStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_key', models.CharField(unique=True, max_length=40, db_index=True)),
                ('attempted', models.IntegerField(default=0)),
                ('failed', models.IntegerField(default=0)),
                ('succeded', models.IntegerField(default=0)),
                ('time_requested', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BrandingSettings',
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
                ('client_id', models.IntegerField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClientCustomization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('client_id', models.IntegerField(unique=True, db_index=True)),
                ('hex_notification', models.CharField(max_length=7)),
                ('hex_notification_text', models.CharField(max_length=7)),
                ('hex_background_bar', models.CharField(max_length=7)),
                ('hex_program_name', models.CharField(max_length=7)),
                ('hex_navigation_icons', models.CharField(max_length=7)),
                ('hex_course_title', models.CharField(max_length=7)),
                ('hex_page_background', models.CharField(max_length=7)),
                ('client_logo', models.CharField(max_length=200)),
                ('identity_provider', models.CharField(max_length=200, blank=True)),
                ('client_background', models.CharField(max_length=200)),
                ('client_background_css', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClientNavLinks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('client_id', models.IntegerField(db_index=True)),
                ('link_name', models.CharField(max_length=200)),
                ('link_label', models.CharField(max_length=200)),
                ('link_url', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompanyContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company_id', models.IntegerField(db_index=True)),
                ('contact_type', models.CharField(max_length=1, choices=[('0', 'Executive Sponsor'), ('1', 'IT Security Contact'), ('2', 'Senior HR/PD Professional'), ('3', 'Day-to-Day Coordinator')])),
                ('full_name', models.CharField(max_length=200, blank=True)),
                ('title', models.CharField(max_length=200, blank=True)),
                ('email', models.CharField(max_length=200, blank=True)),
                ('phone', models.CharField(max_length=200, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompanyInvoicingDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company_id', models.IntegerField(unique=True, db_index=True)),
                ('full_name', models.CharField(max_length=200, blank=True)),
                ('title', models.CharField(max_length=200, blank=True)),
                ('address1', models.CharField(max_length=200, blank=True)),
                ('address2', models.CharField(max_length=200, blank=True)),
                ('city', models.CharField(max_length=200, blank=True)),
                ('state', models.CharField(max_length=200, blank=True)),
                ('postal_code', models.CharField(max_length=200, blank=True)),
                ('country', models.CharField(max_length=200, blank=True)),
                ('po', models.CharField(max_length=200, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DashboardAdminQuickFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now=True, db_index=True)),
                ('user_id', models.IntegerField(db_index=True)),
                ('program_id', models.IntegerField()),
                ('course_id', models.CharField(max_length=200, null=True, blank=True)),
                ('company_id', models.IntegerField(null=True, blank=True)),
                ('group_work_project_id', models.CharField(max_length=300, null=True, blank=True)),
            ],
            options={
                'ordering': ('date_created',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('subject', models.CharField(max_length=256)),
                ('body', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LearnerDashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=80, blank=True)),
                ('description', models.CharField(max_length=5000, blank=True)),
                ('title_color', models.CharField(default=b'#FFFFFF', max_length=20, blank=True)),
                ('description_color', models.CharField(default=b'#FFFFFF', max_length=20, blank=True)),
                ('client_id', models.IntegerField(unique=True)),
                ('course_id', models.CharField(max_length=500)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LearnerDashboardDiscovery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link', models.URLField(null=True, blank=True)),
                ('title', models.CharField(max_length=5000, null=True, blank=True)),
                ('author', models.CharField(max_length=5000, null=True, blank=True)),
                ('position', models.IntegerField(default=100)),
                ('learner_dashboard', models.ForeignKey(to='admin_apros.LearnerDashboard', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LearnerDashboardTile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=20, blank=True)),
                ('title', models.CharField(max_length=40, blank=True)),
                ('link', models.CharField(max_length=500)),
                ('position', models.IntegerField(default=100)),
                ('background_image', models.ImageField(upload_to=b'images/learner_dashboard/tile_backgrounds/', blank=True)),
                ('note', models.CharField(max_length=40, blank=True)),
                ('label_color', models.CharField(default=b'#000000', max_length=20, blank=True)),
                ('title_color', models.CharField(default=b'#3384CA', max_length=20, blank=True)),
                ('note_color', models.CharField(default=b'#868685', max_length=20, blank=True)),
                ('tile_background_color', models.CharField(default=b'#FFFFFF', max_length=20, blank=True)),
                ('tile_type', models.CharField(max_length=1, choices=[('1', 'Article'), ('2', 'Lesson'), ('3', 'Module'), ('4', 'Course')])),
                ('learner_dashboard', models.ForeignKey(to='admin_apros.LearnerDashboard', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TileBookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.IntegerField(unique=True)),
                ('lesson_link', models.CharField(max_length=2000, null=True, blank=True)),
                ('learner_dashboard', models.ForeignKey(to='admin_apros.LearnerDashboard', on_delete=models.CASCADE)),
                ('tile', models.ForeignKey(to='admin_apros.LearnerDashboardTile', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserRegistrationBatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_key', models.CharField(unique=True, max_length=40, db_index=True)),
                ('attempted', models.IntegerField(default=0)),
                ('failed', models.IntegerField(default=0)),
                ('succeded', models.IntegerField(default=0)),
                ('time_requested', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserRegistrationError',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_key', models.CharField(max_length=40, db_index=True)),
                ('error', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='companycontact',
            unique_together=set([('company_id', 'contact_type')]),
        ),
        migrations.AlterUniqueTogether(
            name='clientnavlinks',
            unique_together=set([('client_id', 'link_name')]),
        ),
    ]
