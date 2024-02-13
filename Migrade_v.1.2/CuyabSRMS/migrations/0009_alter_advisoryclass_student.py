# Generated by Django 4.2.7 on 2024-02-13 04:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "CuyabSRMS",
            "0008_rename_initial_grades_advisoryclass_first_quarter_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="advisoryclass",
            name="student",
            field=models.ForeignKey(
                limit_choices_to={"class_type": "advisory"},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="CuyabSRMS.student",
            ),
        ),
    ]
