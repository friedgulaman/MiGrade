# Generated by Django 4.2.5 on 2023-12-27 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0034_remove_gradescores_quarterly_assessment_scores_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='gradescores',
            name='quarterly_assessment_scores',
            field=models.JSONField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gradescores',
            name='scores_hps_quarterly',
            field=models.JSONField(default=1),
            preserve_default=False,
        ),
    ]
