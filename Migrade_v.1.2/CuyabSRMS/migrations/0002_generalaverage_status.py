# Generated by Django 4.2.7 on 2024-03-19 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalaverage',
            name='status',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]