# Generated by Django 4.2.6 on 2023-11-16 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0011_classrecord_quarters'),
    ]

    operations = [
        migrations.AddField(
            model_name='gradescores',
            name='grade',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='gradescores',
            name='section',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]