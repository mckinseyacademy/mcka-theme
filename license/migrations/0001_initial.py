# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LicenseGrant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('license_uuid', models.CharField(max_length=36)),
                ('granted_id', models.IntegerField()),
                ('grantor_id', models.IntegerField()),
                ('grantee_id', models.IntegerField(null=True, blank=True)),
                ('granted_on', models.DateTimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
