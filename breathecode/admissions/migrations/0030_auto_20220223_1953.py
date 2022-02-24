# Generated by Django 3.2.9 on 2022-02-23 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0029_auto_20211217_0248'),
    ]

    operations = [
        migrations.AddField(
            model_name='cohort',
            name='current_module',
            field=models.IntegerField(
                blank=True,
                default=None,
                help_text=
                'The syllabus is separated by modules, from 1 to N and the teacher decides when to start a new mobule (after a couple of days)',
                null=True),
        ),
        migrations.AlterField(
            model_name='cohort',
            name='current_day',
            field=models.IntegerField(
                help_text='Each day the teacher takes attendancy and increases the day in one'),
        ),
    ]