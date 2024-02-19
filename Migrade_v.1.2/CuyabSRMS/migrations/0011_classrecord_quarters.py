# Generated by Django 4.2.6 on 2023-11-16 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0010_merge_0008_subject_0009_alter_activitylog_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassRecord',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('grade', models.CharField(blank=True, max_length=50, null=True)),
                ('section', models.CharField(blank=True, max_length=50, null=True)),
                ('subject', models.CharField(blank=True, max_length=50, null=True)),
                ('teacher', models.CharField(blank=True, max_length=50, null=True)),
                ('quarters', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Quarters',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quarters', models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
    ]