# Generated by Django 4.2.5 on 2024-02-23 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0021_alter_student_teacher'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advisoryclass',
            name='first_quarter',
        ),
        migrations.RemoveField(
            model_name='advisoryclass',
            name='fourth_quarter',
        ),
        migrations.RemoveField(
            model_name='advisoryclass',
            name='from_teacher_id',
        ),
        migrations.RemoveField(
            model_name='advisoryclass',
            name='second_quarter',
        ),
        migrations.RemoveField(
            model_name='advisoryclass',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='advisoryclass',
            name='third_quarter',
        ),
        migrations.AddField(
            model_name='advisoryclass',
            name='grades_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
