# Generated by Django 4.2.5 on 2024-01-28 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0045_merge_20240128_1145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='finalgrade',
            name='quarter1',
        ),
        migrations.RemoveField(
            model_name='finalgrade',
            name='quarter2',
        ),
        migrations.RemoveField(
            model_name='finalgrade',
            name='quarter3',
        ),
        migrations.RemoveField(
            model_name='finalgrade',
            name='quarter4',
        ),
        migrations.RemoveField(
            model_name='finalgrade',
            name='subject',
        ),
        migrations.AlterField(
            model_name='finalgrade',
            name='final_grade',
            field=models.JSONField(),
        ),
    ]
