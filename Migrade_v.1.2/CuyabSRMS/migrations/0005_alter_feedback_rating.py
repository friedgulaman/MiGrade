# Generated by Django 4.2.7 on 2024-04-02 17:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("CuyabSRMS", "0004_feedback"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feedback",
            name="rating",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]