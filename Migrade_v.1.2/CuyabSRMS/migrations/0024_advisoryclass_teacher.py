# Generated by Django 4.2.5 on 2024-02-25 17:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0023_archivedadvisoryclass_remove_quarterly_grade_student_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisoryclass',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='CuyabSRMS.teacher'),
        ),
    ]
