# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_apros', '0010_remove_courserun_course_id_sso'),
    ]

    operations = [
        migrations.AddField(
            model_name='courserun',
            name='access_key_link',
            field=models.URLField(default='test'),
            preserve_default=False,
        ),
    ]
