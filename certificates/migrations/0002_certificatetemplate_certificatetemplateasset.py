# -*- coding: utf-8 -*-


from django.db import migrations, models
import certificates.models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('template', models.TextField()),
                ('course_id', models.CharField(unique=True, max_length=200, db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CertificateTemplateAsset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('asset', models.FileField(max_length=255, upload_to=certificates.models.template_assets_path)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
