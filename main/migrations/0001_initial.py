# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CuratedContentItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_id', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('body', models.CharField(max_length=1000, null=True, blank=True)),
                ('source', models.CharField(max_length=255, null=True, blank=True)),
                ('byline', models.CharField(max_length=255, null=True, blank=True)),
                ('byline_title', models.CharField(max_length=255, null=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('thumbnail_url', models.URLField(null=True, blank=True)),
                ('image_url', models.URLField(null=True, blank=True)),
                ('twitter_username', models.CharField(max_length=255, null=True, blank=True)),
                ('sequence', models.IntegerField()),
                ('created_at', models.DateTimeField(null=True, blank=True)),
                ('display_date', models.DateTimeField(null=True, blank=True)),
                ('content_type', models.CharField(default=b'txt', max_length=3, choices=[(b'txt', b'text'), (b'vid', b'video'), (b'quo', b'quote'), (b'twt', b'tweet'), (b'art', b'article'), (b'img', b'img')])),
            ],
            options={
                'db_table': 'curated_content_item',
            },
            bases=(models.Model,),
        ),
    ]
