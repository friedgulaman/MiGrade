# Generated by Django 4.2.5 on 2023-11-01 07:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("CuyabSRMS", "0003_customuser_profile_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="profile_image",
            field=models.ImageField(
                default="/static/star-admin/images/default_profile_img.jpg",
                upload_to="profile_images/",
            ),
        ),
    ]