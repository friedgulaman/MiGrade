# Generated by Django 4.2.5 on 2023-11-05 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0006_extracteddata_name_of_school'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gradescores',
            name='quarterly_assessment_scores',
            field=models.JSONField(),
        ),
    ]
