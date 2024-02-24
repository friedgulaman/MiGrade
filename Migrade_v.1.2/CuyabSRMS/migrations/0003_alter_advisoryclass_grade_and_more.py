# Generated by Django 4.2.7 on 2024-02-22 15:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("CuyabSRMS", "0002_alter_advisoryclass_grade_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="advisoryclass",
            name="grade",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="archivedclassrecord",
            name="grade",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="archivedclassrecord",
            name="quarters",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="classrecord",
            name="grade",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="classrecord",
            name="quarters",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="finalgrade",
            name="grade",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="generalaverage",
            name="grade",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="grade",
            name="name",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="quarterlygrades",
            name="quarter",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="quarters",
            name="quarters",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="section",
            name="grade",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sections",
                to="CuyabSRMS.grade",
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="grade",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]