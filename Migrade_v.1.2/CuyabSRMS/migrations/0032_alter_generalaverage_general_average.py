# Generated by Django 4.2.6 on 2023-12-15 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0031_generalaverage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalaverage',
            name='general_average',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
