# Generated by Django 4.2.5 on 2023-12-11 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0025_alter_classrecord_quarters'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classrecord',
            name='quarters',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
