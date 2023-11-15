

from django.db import migrations, models


class Migration(migrations.Migration):


    dependencies = [
        ('CuyabSRMS', '0012_merge_20231109_2032'),
    ]

    operations = [

    dependencies = [
        ("CuyabSRMS", "0012_merge_20231109_2037"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="quarters",
            name="first_quarter",
        ),
        migrations.RemoveField(
            model_name="quarters",
            name="fourth_quarter",
        ),
        migrations.RemoveField(
            model_name="quarters",
            name="second_quarter",
        ),
        migrations.RemoveField(
            model_name="quarters",
            name="third_quarter",
        ),
        migrations.AddField(
            model_name="quarters",
            name="quarters",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),

    ]
