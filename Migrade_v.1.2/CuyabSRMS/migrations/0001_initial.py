# Generated by Django 4.2.7 on 2024-02-19 15:44

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="AcceptedMessage",
            fields=[
                ("message_id", models.IntegerField(primary_key=True, serialize=False)),
                ("file_name", models.CharField(max_length=255)),
                ("json_data", models.JSONField()),
                ("accepted_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Announcement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                ("content", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="ArchivedClassRecord",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("grade", models.CharField(blank=True, max_length=50, null=True)),
                ("section", models.CharField(blank=True, max_length=50, null=True)),
                ("subject", models.CharField(blank=True, max_length=50, null=True)),
                ("quarters", models.CharField(blank=True, max_length=50, null=True)),
                ("date_archived", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="ClassRecord",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("grade", models.CharField(blank=True, max_length=50, null=True)),
                ("section", models.CharField(blank=True, max_length=50, null=True)),
                ("subject", models.CharField(blank=True, max_length=50, null=True)),
                ("quarters", models.CharField(blank=True, max_length=50, null=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Grade",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="InboxMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("to_teacher", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "from_teacher",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("file_name", models.CharField(blank=True, max_length=50, null=True)),
                ("json_data", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Quarters",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("quarters", models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="SchoolInformation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("region", models.CharField(max_length=100)),
                ("division", models.CharField(max_length=100)),
                ("school_id", models.CharField(max_length=100)),
                ("school_name", models.CharField(max_length=200)),
                ("district", models.CharField(max_length=100)),
                ("school_year", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Subject",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("written_works_percentage", models.PositiveIntegerField(default=40)),
                (
                    "performance_task_percentage",
                    models.PositiveIntegerField(default=40),
                ),
                (
                    "quarterly_assessment_percentage",
                    models.PositiveIntegerField(default=20),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "user_type",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "Admin"), (2, "Teacher")]
                    ),
                ),
                ("middle_ini", models.CharField(blank=True, max_length=1, null=True)),
                (
                    "profile_image",
                    models.ImageField(
                        default="profile_images/default_profile_img.jpg",
                        upload_to="profile_images/",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Teacher",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("grade_section", models.JSONField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("lrn", models.CharField(max_length=12)),
                (
                    "sex",
                    models.CharField(
                        choices=[("M", "Male"), ("F", "Female")], max_length=1
                    ),
                ),
                ("birthday", models.CharField(default="N/A", max_length=10)),
                ("school_id", models.CharField(blank=True, max_length=50, null=True)),
                ("division", models.CharField(blank=True, max_length=255, null=True)),
                ("district", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "school_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("school_year", models.CharField(blank=True, max_length=50, null=True)),
                ("grade", models.CharField(blank=True, max_length=50, null=True)),
                ("section", models.CharField(blank=True, max_length=50, null=True)),
                ("class_type", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.teacher",
                    ),
                ),
            ],
            options={
                "unique_together": {("lrn", "teacher")},
            },
        ),
        migrations.CreateModel(
            name="Section",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=50, null=True)),
                ("total_students", models.PositiveIntegerField(default=0)),
                ("class_type", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "grade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sections",
                        to="CuyabSRMS.grade",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sections",
                        to="CuyabSRMS.teacher",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="QuarterlyGrades",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quarter", models.CharField(max_length=100)),
                ("grades", models.JSONField(null=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.student",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProcessedDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("document", models.FileField(upload_to="processed_documents/")),
                ("upload_date", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GradeScores",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("scores_hps_written", models.JSONField()),
                ("scores_hps_performance", models.JSONField()),
                ("total_ww_hps", models.FloatField(blank=True, null=True)),
                ("total_pt_hps", models.FloatField(blank=True, null=True)),
                ("total_qa_hps", models.FloatField(blank=True, null=True)),
                ("written_works_scores", models.JSONField()),
                ("performance_task_scores", models.JSONField()),
                ("initial_grades", models.FloatField(blank=True, null=True)),
                ("transmuted_grades", models.FloatField(blank=True, null=True)),
                ("total_score_written", models.FloatField(blank=True, null=True)),
                ("total_max_score_written", models.FloatField(blank=True, null=True)),
                ("total_score_performance", models.FloatField(blank=True, null=True)),
                (
                    "total_max_score_performance",
                    models.FloatField(blank=True, null=True),
                ),
                ("total_score_quarterly", models.FloatField(blank=True, null=True)),
                ("total_max_score_quarterly", models.FloatField(blank=True, null=True)),
                ("percentage_score_written", models.FloatField(blank=True, null=True)),
                (
                    "percentage_score_performance",
                    models.FloatField(blank=True, null=True),
                ),
                (
                    "percentage_score_quarterly",
                    models.FloatField(blank=True, null=True),
                ),
                ("weight_input_written", models.FloatField(blank=True, null=True)),
                ("weight_input_performance", models.FloatField(blank=True, null=True)),
                ("weight_input_quarterly", models.FloatField(blank=True, null=True)),
                ("weighted_score_written", models.FloatField(blank=True, null=True)),
                (
                    "weighted_score_performance",
                    models.FloatField(blank=True, null=True),
                ),
                ("weighted_score_quarterly", models.FloatField(blank=True, null=True)),
                (
                    "class_record",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="GradeScores",
                        to="CuyabSRMS.classrecord",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.student",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GeneralAverage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("grade", models.CharField(max_length=50)),
                ("section", models.CharField(max_length=50)),
                ("general_average", models.FloatField(blank=True, null=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.student",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FinalGrade",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("grade", models.CharField(max_length=50)),
                ("section", models.CharField(max_length=50)),
                ("subject", models.CharField(blank=True, max_length=50, null=True)),
                ("final_grade", models.JSONField()),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.student",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.teacher",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExtractedData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("last_name", models.CharField(blank=True, max_length=255, null=True)),
                ("first_name", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "middle_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("lrn", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "school_year",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("birthdate", models.DateField(blank=True, null=True)),
                (
                    "classified_as_grade",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "general_average",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("sex", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "name_of_school",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "processed_document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.processeddocument",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="classrecord",
            name="teacher",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="CuyabSRMS.teacher"
            ),
        ),
        migrations.CreateModel(
            name="ArchivedStudent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("archived_name", models.CharField(max_length=255)),
                ("archived_lrn", models.CharField(max_length=12)),
                (
                    "archived_sex",
                    models.CharField(
                        choices=[("M", "Male"), ("F", "Female")], max_length=1
                    ),
                ),
                ("archived_birthday", models.CharField(default="N/A", max_length=10)),
                (
                    "archived_school_id",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "archived_division",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "archived_district",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "archived_school_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "archived_school_year",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "archived_grade",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "archived_section",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "archived_teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.teacher",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArchivedQuarterlyGrades",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("archived_quarter", models.CharField(max_length=100)),
                ("archived_grades", models.JSONField(null=True)),
                (
                    "archived_student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.archivedstudent",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArchivedGradeScores",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("scores_hps_written", models.JSONField()),
                ("scores_hps_performance", models.JSONField()),
                ("total_ww_hps", models.FloatField(blank=True, null=True)),
                ("total_pt_hps", models.FloatField(blank=True, null=True)),
                ("total_qa_hps", models.FloatField(blank=True, null=True)),
                ("written_works_scores", models.JSONField()),
                ("performance_task_scores", models.JSONField()),
                ("initial_grades", models.FloatField(blank=True, null=True)),
                ("transmuted_grades", models.FloatField(blank=True, null=True)),
                ("total_score_written", models.FloatField(blank=True, null=True)),
                ("total_max_score_written", models.FloatField(blank=True, null=True)),
                ("total_score_performance", models.FloatField(blank=True, null=True)),
                (
                    "total_max_score_performance",
                    models.FloatField(blank=True, null=True),
                ),
                ("total_score_quarterly", models.FloatField(blank=True, null=True)),
                ("total_max_score_quarterly", models.FloatField(blank=True, null=True)),
                ("percentage_score_written", models.FloatField(blank=True, null=True)),
                (
                    "percentage_score_performance",
                    models.FloatField(blank=True, null=True),
                ),
                (
                    "percentage_score_quarterly",
                    models.FloatField(blank=True, null=True),
                ),
                ("weight_input_written", models.FloatField(blank=True, null=True)),
                ("weight_input_performance", models.FloatField(blank=True, null=True)),
                ("weight_input_quarterly", models.FloatField(blank=True, null=True)),
                ("weighted_score_written", models.FloatField(blank=True, null=True)),
                (
                    "weighted_score_performance",
                    models.FloatField(blank=True, null=True),
                ),
                ("weighted_score_quarterly", models.FloatField(blank=True, null=True)),
                (
                    "archived_class_record",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="archived_gradescores",
                        to="CuyabSRMS.archivedclassrecord",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.archivedstudent",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArchivedGeneralAverage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("archived_grade", models.CharField(max_length=50)),
                ("archived_section", models.CharField(max_length=50)),
                ("archived_general_average", models.FloatField(blank=True, null=True)),
                (
                    "archived_student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.archivedstudent",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArchivedFinalGrade",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("archived_grade", models.CharField(max_length=50)),
                ("archived_section", models.CharField(max_length=50)),
                ("archived_final_grade", models.JSONField()),
                (
                    "archived_student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.archivedstudent",
                    ),
                ),
                (
                    "archived_teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.teacher",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="archivedclassrecord",
            name="teacher",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="CuyabSRMS.teacher"
            ),
        ),
        migrations.CreateModel(
            name="AdvisoryClass",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("grade", models.CharField(blank=True, max_length=50, null=True)),
                ("section", models.CharField(blank=True, max_length=50, null=True)),
                ("subject", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "first_quarter",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                (
                    "second_quarter",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                (
                    "third_quarter",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                (
                    "fourth_quarter",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                (
                    "from_teacher_id",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "student",
                    models.ForeignKey(
                        limit_choices_to={"class_type": "advisory"},
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="CuyabSRMS.student",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Admin",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("password", models.CharField(max_length=225)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "username",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ActivityLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                ("action", models.CharField(max_length=255)),
                ("details", models.TextField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
