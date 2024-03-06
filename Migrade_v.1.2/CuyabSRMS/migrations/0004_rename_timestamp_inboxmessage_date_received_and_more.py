# Generated by Django 4.2.7 on 2024-03-02 16:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("CuyabSRMS", "0003_acceptedmessage_reviewed_by_inboxmessage_accepted_by"),
    ]

    operations = [
        migrations.RenameField(
            model_name="inboxmessage",
            old_name="timestamp",
            new_name="date_received",
        ),
        migrations.AddField(
            model_name="inboxmessage",
            name="date_accepted",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
