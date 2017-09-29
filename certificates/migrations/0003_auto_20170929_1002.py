# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import certificates.models
import upload_validator


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0002_certificatetemplate_certificatetemplateasset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificatetemplate',
            name='course_id',
            field=models.CharField(unique=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='certificatetemplateasset',
            name='asset',
            field=models.FileField(max_length=255, upload_to=certificates.models.template_assets_path, validators=[upload_validator.FileTypeValidator(allowed_types=[b'image/jpeg', b'image/png', b'image/gif', b'text/css', b'text/plain', b'application/javascript'])]),
        ),
    ]
