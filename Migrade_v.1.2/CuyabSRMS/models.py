# models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, "Admin"),
        (2, "Teacher"), 
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    middle_ini = models.CharField(max_length=1, blank=True, null=True)  # Add the middle_ini field here
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default_profile_img.jpg')

    def __str__(self):
        return self.username  # You can choose any field that you want to display here
    
class Admin(models.Model):
    username = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=225)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Admin: {self.username.username}, Email: {self.email}, Created: {self.created_at}"

class Teacher(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Teacher: {self.first_name} {self.last_name}, Email: {self.email}, Middle Initial: {self.middle_ini}, Created: {self.created_at}"

class Student(models.Model):
    name = models.CharField(max_length=255)
    lrn = models.CharField(max_length=12, unique=True)
    sex = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
    birthday = models.CharField(max_length=10, default='N/A' )
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    grade = models.CharField(max_length=50, null=True, blank=True)
    section = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name
    
class Grade(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Section(models.Model):
    name = models.CharField(max_length=50)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='sections')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='sections')

    def __str__(self):
        return self.name


class GradeScores(models.Model):
    student_name = models.CharField(max_length=255, null=True, blank=True)
    written_works_scores = models.JSONField()
    performance_task_scores = models.JSONField()
    quarterly_assessment_scores = models.FloatField(default=0)
    initial_grades = models.FloatField(default=0)
    transmuted_grades = models.FloatField(default=0)
    total_score_written = models.FloatField(default=0)
    total_max_score_written = models.FloatField(default=0)
    total_score_performance = models.FloatField(default=0)
    total_max_score_performance = models.FloatField(default=0)
    total_score_quarterly = models.FloatField(default=0)   
    total_max_score_quarterly = models.FloatField(default=0)
    percentage_score_written = models.FloatField(default=0)
    percentage_score_performance = models.FloatField(default=0)
    percentage_score_quarterly = models.FloatField(default=0)
    weighted_score_written = models.FloatField(default=0)
    weighted_score_performance = models.FloatField(default=0)
    weighted_score_quarterly = models.FloatField(default=0)


    def __str__(self):
        return self.student_name



@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.user_type == 2:  # Check if the user is a teacher
        Teacher.objects.create(user=instance)  # Create a Teacher object associated with the CustomUser

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.teacher.save()


class ProcessedDocument(models.Model):
    document = models.FileField(upload_to='processed_documents/')
    upload_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)


    def __str__(self):
        return self.document.name

class ExtractedData(models.Model):
    processed_document = models.OneToOneField(ProcessedDocument, on_delete=models.CASCADE)
    region = models.CharField(max_length=255, blank=True, null=True)
    division = models.CharField(max_length=255, blank=True, null=True)
    school_year = models.CharField(max_length=255, blank=True, null=True)
    school_name = models.CharField(max_length=255, blank=True, null=True)
    school_id = models.CharField(max_length=10, blank=True, null=True)
    grade_section = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True)  # Add new field for last name
    first_name = models.CharField(max_length=255, blank=True)  # Add new field for first name
    middle_name = models.CharField(max_length=255, blank=True)  # Add new field for middle name

    def save_extracted_data(self, key_value_pairs):
        self.region = key_value_pairs.get("REGION", "")
        self.division = key_value_pairs.get("DIVISION", "")
        self.school_year = key_value_pairs.get("SCHOOL YEAR", "")
        self.school_name = key_value_pairs.get("SCHOOL NAME", "")
        self.school_id = key_value_pairs.get("SCHOOL ID", "")
        self.grade_section = key_value_pairs.get("GRADE & SECTION", "")
        self.last_name = key_value_pairs.get("LAST NAME", "")  # Extracted last name
        self.first_name = key_value_pairs.get("FIRST NAME", "")  # Extracted first name
        self.middle_name = key_value_pairs.get("MIDDLE NAME", "")
        self.save()

    def to_json(self):
        return {
            "region": self.region,
            "division": self.division,
            "school_year": self.school_year,
            "school_name": self.school_name,
            "school_id": self.school_id,
            "grade_section": self.grade_section
        }

class ActivityLog(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    action = models.CharField(max_length=255)
    details = models.TextField()

    def __str__(self):
        return f'{self.user.username} - {self.action}'