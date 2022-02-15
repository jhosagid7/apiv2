# Generated by Django 3.2.9 on 2021-12-23 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_auto_20211213_0304'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='published',
            new_name='published_date_raw',
        ),
        migrations.AddField(
            model_name='job',
            name='max_salary',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='min_salary',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='published_date_processed',
            field=models.DateField(null=True),
        ),
    ]