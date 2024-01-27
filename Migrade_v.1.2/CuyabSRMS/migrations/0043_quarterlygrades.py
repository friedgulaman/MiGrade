# Generated by Django 4.2.6 on 2024-01-26 02:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0042_remove_generalaverage_student_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuarterlyGrades',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quarter', models.CharField(max_length=100)),
                ('grades', models.JSONField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CuyabSRMS.student')),
            ],
        ),
    ]