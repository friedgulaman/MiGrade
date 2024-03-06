# Generated by Django 4.2.7 on 2024-03-02 15:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CuyabSRMS', '0003_remove_processeddocument_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RestoreRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_requested', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='Pending', max_length=20)),
                ('archived_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CuyabSRMS.archivedclassrecord')),
                ('requester', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='CuyabSRMS.teacher')),
            ],
        ),
    ]
