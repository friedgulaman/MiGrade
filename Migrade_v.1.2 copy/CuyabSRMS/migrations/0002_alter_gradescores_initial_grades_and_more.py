# Generated by Django 4.2.5 on 2023-10-26 03:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("CuyabSRMS", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gradescores",
            name="initial_grades",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="gradescores",
            name="quarterly_assessment_scores",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="gradescores",
            name="transmuted_grades",
            field=models.FloatField(default=0),
        ),
    ]
