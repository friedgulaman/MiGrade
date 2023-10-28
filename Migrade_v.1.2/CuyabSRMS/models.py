# models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.conf import settings

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

