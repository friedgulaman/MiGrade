# Generated by Django 4.2.5 on 2023-11-08 14:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0009_quarters'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quarters',
            old_name='first_quarter',
            new_name='quarters',
        ),
        migrations.RemoveField(
            model_name='quarters',
            name='fourth_quarter',
        ),
        migrations.RemoveField(
            model_name='quarters',
            name='second_quarter',
        ),
        migrations.RemoveField(
            model_name='quarters',
            name='third_quarter',
        ),
    ]