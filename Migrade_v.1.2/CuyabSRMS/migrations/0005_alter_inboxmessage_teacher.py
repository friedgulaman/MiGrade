# Generated by Django 4.2.7 on 2024-02-04 10:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("CuyabSRMS", "0004_inboxmessage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inboxmessage",
            name="teacher",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]