# Generated by Django 4.2.7 on 2024-03-02 15:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("CuyabSRMS", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="inboxmessage",
            name="accepted",
            field=models.BooleanField(default=False),
        ),
    ]
