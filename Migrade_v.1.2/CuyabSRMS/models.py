# models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.conf import settings

from datetime import datetime
import re
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
        return f"Teacher: {self.user.first_name} {self.user.last_name}, Email: {self.user.email}, Created: {self.created_at}"
    
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

class Quarters(models.Model):
    id = models.AutoField(primary_key=True)
    quarters = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.name
    
class Subject(models.Model):
    id = models.AutoField(primary_key=True)  # Adding an 'id' field
    name = models.CharField(max_length=100, unique=True)
    written_works_percentage = models.PositiveIntegerField(default=40)
    performance_task_percentage = models.PositiveIntegerField(default=40)
    quarterly_assessment_percentage = models.PositiveIntegerField(default=20)

    def __str__(self):
        return self.name
    
    
class ClassRecord(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    grade = models.CharField(max_length=50, blank=True, null=True)  # Add a foreign key to Grade
    section = models.CharField(max_length=50, blank=True, null=True) # Add a foreign key to Section
    subject = models.CharField(max_length=50, blank=True, null=True)  # Add a foreign key to Subject
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)  # Add a foreign key to Teacher
    quarters = models.CharField(max_length=50, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)

class GradeScores(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_record = models.ForeignKey(ClassRecord, on_delete=models.CASCADE, related_name='GradeScores')
    scores_hps_written = models.JSONField()  # Adjust with your actual field type
    scores_hps_performance = models.JSONField()  # Adjust with your actual field type
    total_ww_hps = models.FloatField(null=True, blank=True)
    total_pt_hps = models.FloatField(null=True, blank=True)
    total_qa_hps = models.FloatField(null=True, blank=True)
    written_works_scores = models.JSONField()
    performance_task_scores = models.JSONField()
    initial_grades = models.FloatField(null=True, blank=True)
    transmuted_grades = models.FloatField(null=True, blank=True)
    total_score_written = models.FloatField(null=True, blank=True)
    total_max_score_written = models.FloatField(null=True, blank=True)
    total_score_performance = models.FloatField(null=True, blank=True)
    total_max_score_performance = models.FloatField(null=True, blank=True)
    total_score_quarterly = models.FloatField(null=True, blank=True) 
    total_max_score_quarterly = models.FloatField(null=True, blank=True)
    percentage_score_written = models.FloatField(null=True, blank=True)
    percentage_score_performance = models.FloatField(null=True, blank=True)
    percentage_score_quarterly = models.FloatField(null=True, blank=True)
    weight_input_written = models.FloatField(null=True, blank=True)
    weight_input_performance = models.FloatField(null=True, blank=True)
    weight_input_quarterly = models.FloatField(null=True, blank=True)
    weighted_score_written = models.FloatField(null=True, blank=True)
    weighted_score_performance = models.FloatField(null=True, blank=True)
    weighted_score_quarterly = models.FloatField(null=True, blank=True)


    def __str__(self):
        return self.student.name

    
    def get_class_record_id(self):
        # Check if classRecord is not None before accessing its id
        if self.classRecord:
            return self.classRecord.id
        else:
            return None
        
    def get_subject_score(self, subject, quarter):
        # Adjust this based on your actual field names
        field_name = f'scores_{subject.lower()}_{quarter.lower()}'
        print(field_name)
        subject_scores = getattr(self, field_name, None)
        
        # Assuming subject_scores is a dictionary where keys are student names
        # and values are scores, return the score for the current student
        return subject_scores.get(self.student.name, None) if subject_scores else None
    
    

    
class FinalGrade(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Change this line
    grade = models.CharField(max_length=50)
    section = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    quarter1 = models.FloatField()
    quarter2 = models.FloatField()
    quarter3 = models.FloatField()
    quarter4 = models.FloatField()
    final_grade = models.FloatField()

    def __str__(self):
        return f"FinalGrade: {self.student.name} - {self.subject}, Teacher: {self.teacher}"

class GeneralAverage(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    grade = models.CharField(max_length=50)
    section = models.CharField(max_length=50)
    general_average = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.student_name} - {self.grade} - {self.section} - General Average: {self.general_average}"

class QuarterlyGrades(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quarter = models.CharField(max_length=100)
    grades = models.JSONField(null=True)

    def __str__(self):
        return f"{self.student.name}'s grades for {self.quarter}"

    
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

    def save_extracted_data(self, extracted_data):
        self.last_name = extracted_data.get('last_name', '')
        self.first_name = extracted_data.get('first_name', '')
        self.middle_name = extracted_data.get('middle_name', '')
        self.lrn = extracted_data.get('lrn', '')
        self.school_year = extracted_data.get('school_year', '')
        birthdate_str = extracted_data.get('birthdate', '')
        # Convert birthdate string to datetime
        try:
            self.birthdate = datetime.strptime(birthdate_str, "%m/%d/%Y").date()
        except ValueError:
            self.birthdate = None  # Set to None if the birthdate format is invalid
        self.classified_as_grade = extracted_data.get('classified_as_grade', '')
        self.general_average = extracted_data.get('general_average', '')
        self.sex = extracted_data.get('sex', '')
        self.name_of_school = extracted_data.get('name_of_school', '')
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



class ActivityLog(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    action = models.CharField(max_length=255)
    details = models.TextField()

    def __str__(self):
        return f'{self.user.username} - {self.action}'

