# -*- coding: utf-8 -*-


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
            field=models.FileField(max_length=255, upload_to=certificates.models.template_assets_path, validators=[upload_validator.FileTypeValidator(allowed_types=['image/jpeg', 'image/png', 'image/gif', 'text/css', 'text/plain', 'application/javascript'])]),
        ),
    ]
