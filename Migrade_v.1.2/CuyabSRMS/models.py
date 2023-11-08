# models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import datetime
import re

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, "Admin"),
        (2, "Teacher"), 
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    middle_ini = models.CharField(max_length=1, blank=True, null=True)  # Add the middle_ini field here

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
    quarterly_assessment_scores = models.JSONField()
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
    processed_document = models.ForeignKey(ProcessedDocument, on_delete=models.CASCADE)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    lrn = models.CharField(max_length=20, blank=True, null=True)
    school_year = models.CharField(max_length=100, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    classified_as_grade = models.CharField(max_length=100, blank=True, null=True)
    general_average = models.CharField(max_length=100, blank=True, null=True)
    sex = models.CharField(max_length=10, blank=True, null=True)
    name_of_school = models.CharField(max_length=255, blank=True, null=True)

    def save_extracted_data(self, key_value_pairs):
        self.last_name = key_value_pairs.get("LAST NAME", "")
        self.first_name = key_value_pairs.get("FIRST NAME", "")
        self.middle_name = key_value_pairs.get("MIDDLE NAME", "")
        self.lrn = key_value_pairs.get("LRN", "")
        self.school_year = key_value_pairs.get("SCHOOL YEAR", "")
        birthdate_str = key_value_pairs.get("BIRTHDATE", "")
        # Convert birthdate string to datetime
        try:
            self.birthdate = datetime.strptime(birthdate_str, "%m/%d/%Y").date()
        except ValueError:
            self.birthdate = None  # Set to None if the birthdate format is invalid
        self.classified_as_grade = key_value_pairs.get("Classified as Grade:", "")
        self.general_average = key_value_pairs.get("GENERAL AVERAGE", "")
        self.sex = key_value_pairs.get("SEX", "")
        self.name_of_school = key_value_pairs.get("Name_of_School", "")
        self.save()

    def populate_data(self, data):
        self.last_name = data.get('Last_Name', None)
        self.first_name = data.get('First_Name', None)
        self.middle_name = data.get('Middle_Name', None)
        self.sex = data.get('SEX', None)
        self.classified_as_grade = data.get('Classified_as_Grade', None)
        self.lrn = data.get('LRN', None)
        # Add other fields accordingly
        self.birthdate = None  # Initialize it as None
        self.name_of_school = data.get('Name_of_School', None)
        self.school_year = data.get('School_Year', None)
        self.general_average = data.get('General_Average', None)

        birthdate_str = data.get('Birthdate', None)
        if birthdate_str:
            try:
                self.birthdate = datetime.datetime.strptime(birthdate_str, "%m/%d/%Y").date()
            except ValueError as e:
                print(f"Error parsing birthdate: {e}")
        self.save()

    def to_json(self):
        return {
            "last_name": self.last_name,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "lrn": self.lrn,
            "school_year": self.school_year,
            "birthdate": self.birthdate.strftime("%m/%d/%Y") if self.birthdate else None,
            "grade": self.classified_as_grade,
            "general_average": self.general_average,
            "sex": self.sex,
            "name_of_school": self.name_of_school
        }

class Subject(models.Model):
    id = models.AutoField(primary_key=True)  # Adding an 'id' field
    name = models.CharField(max_length=100, unique=True)
    written_works_percentage = models.PositiveIntegerField(default=40)
    performance_task_percentage = models.PositiveIntegerField(default=40)
    quarterly_assessment_percentage = models.PositiveIntegerField(default=20)

    def __str__(self):
        return self.name

class Quarters(models.Model):
    id = models.AutoField(primary_key=True)
    quarters = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.name