# Generated by Django 4.2.7 on 2024-02-04 02:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("CuyabSRMS", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="class_type",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
