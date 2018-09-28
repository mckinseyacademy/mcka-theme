# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0014_companyinvoicingdetails_identity_provider'),
    ]

    operations = [
        migrations.CreateModel(
            name='SelfRegistrationRoles',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('option_text', models.CharField(max_length=500)),
            ],
        ),
        migrations.AddField(
            model_name='courserun',
            name='self_registration_description_text',
            field=models.CharField(default=b'Self Registration Description Text', max_length=2000),
        ),
        migrations.AddField(
            model_name='courserun',
            name='self_registration_page_heading',
            field=models.CharField(default=b'Self Registration Page Heading', max_length=2000),
        ),
        migrations.AddField(
            model_name='selfregistrationroles',
            name='course_run',
            field=models.ForeignKey(to='admin_apros.CourseRun', on_delete=models.CASCADE),
        ),
    ]
