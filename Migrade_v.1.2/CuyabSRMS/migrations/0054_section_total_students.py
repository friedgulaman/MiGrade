# Generated by Django 4.2.6 on 2024-02-02 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0053_merge_20240202_2315'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='total_students',
            field=models.PositiveIntegerField(default=0),
        ),
    ]