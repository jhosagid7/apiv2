# Generated by Django 3.2.9 on 2022-02-18 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0031_merge_0030_alter_event_host_0030_auto_20220111_0518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='url',
            field=models.URLField(
                blank=True,
                default=None,
                help_text=
                'URL can be blank if the event will be synched with EventBrite, it will be filled automatically by the API.',
                max_length=255,
                null=True),
        ),
    ]
