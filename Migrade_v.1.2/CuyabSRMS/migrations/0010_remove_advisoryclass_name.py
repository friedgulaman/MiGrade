# Generated by Django 4.2.7 on 2024-02-13 05:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("CuyabSRMS", "0009_alter_advisoryclass_student"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="advisoryclass",
            name="name",
        ),
    ]
