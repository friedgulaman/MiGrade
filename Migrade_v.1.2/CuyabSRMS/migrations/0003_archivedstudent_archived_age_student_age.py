# Generated by Django 4.2.7 on 2024-03-22 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0002_generalaverage_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='archivedstudent',
            name='archived_age',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='age',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
