# models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.conf import settings
import json
from datetime import datetime
import re
from django.utils import timezone
from django.db import transaction
import os
from django.db.models import Avg
from django.db.models import F, Subquery, OuterRef, Value
from django.db.models.functions import Cast

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, "Super"),
        (2, "Teacher"), 
        (3, "Admin"),
        (4, "MT"),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    middle_ini = models.CharField(max_length=1, blank=True, null=True)  # Add the middle_ini field here
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default_profile_img.jpg')

    def __str__(self):
        return self.username

class SuperAdmin(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SuperAdmin: {self.user.first_name} {self.user.last_name}, Email: {self.user.email}, Created: {self.created_at}"

class Admin(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Admin: {self.user.first_name} {self.user.last_name}, Email: {self.user.email}, Created: {self.created_at}"

class MT(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_grades = models.JSONField(default=list, null=True, blank=True)  # JSONField to store assigned grades

    def __str__(self):
        return f"MT: {self.user.username}, Created: {self.created_at}"

class Teacher(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    grade_section = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Teacher: {self.user.first_name} {self.user.last_name}, Email: {self.user.email}, Created: {self.created_at}"
    
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 2:  # Check if the user is a teacher
            Teacher.objects.create(user=instance)  # Create a Teacher object associated with the CustomUser
        elif instance.user_type == 3:
            Admin.objects.create(user=instance)
        elif instance.user_type == 4:
            MT.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        super_admin, created = SuperAdmin.objects.get_or_create(user=instance)
    elif instance.user_type == 3:
        admin, created = Admin.objects.get_or_create(user=instance)
    elif instance.user_type == 4:
        mt, created = MT.objects.get_or_create(user=instance)


class SchoolInformation(models.Model):
    region = models.CharField(max_length=100)
    division = models.CharField(max_length=100)
    school_id = models.CharField(max_length=100)
    school_name = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    school_year = models.CharField(max_length=100)
    principal_name = models.CharField(max_length=100)
    

class Student(models.Model):
    
    name = models.CharField(max_length=255)
    lrn = models.CharField(max_length=12)
    sex = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
    birthday = models.CharField(max_length=10, default='N/A')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    school_id = models.CharField(max_length=50, null=True, blank=True)
    age = models.CharField(max_length=50, null=True, blank=True)
    division = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    school_name = models.CharField(max_length=255, null=True, blank=True)
    school_year = models.CharField(max_length=50, null=True, blank=True)
    grade = models.CharField(max_length=50, null=True, blank=True)
    section = models.CharField(max_length=50, null=True, blank=True)
    class_type = models.JSONField(null=True)  # New field for class type

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('lrn', 'teacher')


    
    def archive(self):
        # Create an instance of ArchivedStudent before deleting the student
        archived_student = ArchivedStudent.objects.create(
            original_student=self,
            archived_name=self.name,
            archived_lrn=self.lrn,
            archived_sex=self.sex,
            archived_birthday=self.birthday,
            archived_teacher=self.teacher,
            archived_school_id=self.school_id,
            archived_division=self.division,
            archived_district=self.district,
            archived_school_name=self.school_name,
            archived_school_year=self.school_year,
            archived_grade=self.grade,
            archived_section=self.section,
            archived_class_type=self.class_type
        )

        # Delete the student after archiving
        self.delete()

        # Return the archived student instance
        return archived_student

class ArchivedStudent(models.Model):
    archived_name = models.CharField(max_length=255)
    archived_lrn = models.CharField(max_length=12)
    archived_sex = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
    archived_birthday = models.CharField(max_length=10, default='N/A')
    archived_teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, null=True)
    archived_school_id = models.CharField(max_length=50, null=True, blank=True)
    archived_age = models.CharField(max_length=50, null=True, blank=True)
    archived_division = models.CharField(max_length=255, null=True, blank=True)
    archived_district = models.CharField(max_length=255, null=True, blank=True)
    archived_school_name = models.CharField(max_length=255, null=True, blank=True)
    archived_school_year = models.CharField(max_length=50, null=True, blank=True)
    archived_grade = models.CharField(max_length=50, null=True, blank=True) 
    archived_section = models.CharField(max_length=50, null=True, blank=True)
    archived_class_type = models.JSONField(null=True)  # New field for class type

    def __str__(self):
        return f"Archived Student: {self.archived_name}"
    
    def restore(self):
        # Create a new Student instance based on archived data
        restored_student = Student.objects.create(
            name=self.archived_name,
            lrn=self.archived_lrn,
            sex=self.archived_sex,
            birthday=self.archived_birthday,
            teacher=self.archived_teacher,
            school_id=self.archived_school_id,
            division=self.archived_division,
            district=self.archived_district,
            school_name=self.archived_school_name,
            school_year=self.archived_school_year,
            grade=self.archived_grade,
            section=self.archived_section,
            class_type=self.archived_class_type
            # Populate other fields as needed
        )
        # Delete the ArchivedStudent instance after restoration
        self.delete()
        return restored_student
    
class Grade(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

class Section(models.Model):
    
    name = models.CharField(max_length=50, null=True, blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='sections')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='sections')
    total_students = models.PositiveIntegerField(default=0)
    class_type = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class Quarters(models.Model):

    id = models.AutoField(primary_key=True)
    quarters = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.name
    
class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    assessment = models.JSONField(null=True, blank=True)  # JSONField for assessment

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
    school_year = models.CharField(max_length=50, null=True)
    

    def archive(self):
        try:
            with transaction.atomic():
                # Archive related GradeScores
                for gradescore in self.gradescores.all():
                     ArchivedGradeScores.objects.create(
                        archived_class_record=self,
                        student=gradescore.student,
                        initial_grades=gradescore.initial_grades,
                        transmuted_grades=gradescore.transmuted_grades,
                        grade_scores=gradescore.grade_scores,
                    )

                # Archive ClassRecord
                ArchivedClassRecord.objects.create(
                    name=self.name,
                    grade=self.grade,
                    section=self.section,
                    subject=self.subject,
                    teacher=self.teacher,
                    quarters=self.quarters,
                    date_archived=self.date_modified,
                    school_year=self.school_year
                )

                # Delete the ClassRecord instance after archiving
                self.delete()

                return True  # Return True if archiving is successful
        except Exception as e:
            print(f"Error occurred during archiving: {str(e)}")
            return False  # Return False if archiving fails



class ArchivedClassRecord(models.Model):
    

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    grade = models.CharField(max_length=50, blank=True, null=True)
    section = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=50, blank=True, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    quarters = models.CharField(max_length=50, blank=True, null=True)
    date_archived = models.DateTimeField(auto_now_add=True)  # Record the date when the record was archived
    school_year = models.CharField(max_length=50, null=True)
    # is_restore_approved = models.BooleanField(null=True)

    def restore(self):
        try:
            with transaction.atomic():
                # Create a new instance of the ClassRecord using archived data
                class_record = ClassRecord.objects.create(
                    name=self.name,
                    grade=self.grade,
                    section=self.section,
                    subject=self.subject,
                    teacher=self.teacher,
                    quarters=self.quarters,
                    school_year=self.school_year
                )
                
                # Restore related objects (e.g., GradeScores)
                self.restore_related_objects(class_record)

                # Delete the archived record after restoration
                self.delete()
                
                # Return the restored ClassRecord instance
                return class_record
        except Exception as e:
            # Handle any exceptions that occur during restoration
            # You can log the error or handle it based on your application's requirements
            print(f"Error occurred during restoration: {str(e)}")
            return None

    def restore_related_objects(self, class_record):
        # Restore related GradeScores
        archived_grade_scores = self.archived_gradescores.all()
        for archived_grade_score in archived_grade_scores:
             GradeScores.objects.create(
                student=archived_grade_score.student,
                class_record=class_record,
                initial_grades=archived_grade_score.initial_grades,
                transmuted_grades=archived_grade_score.transmuted_grades,
                grade_scores=archived_grade_score.grade_scores,
            )

class ArchivedGradeScores(models.Model):
    archived_class_record = models.ForeignKey(ArchivedClassRecord, on_delete=models.CASCADE, related_name='archived_gradescores')
    student = models.ForeignKey(ArchivedStudent, on_delete=models.CASCADE)
    initial_grades = models.FloatField(null=True, blank=True)
    transmuted_grades = models.FloatField(null=True, blank=True)
    grade_scores = models.JSONField(null=True, blank=True)



class GradeScores(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_record = models.ForeignKey(ClassRecord, on_delete=models.CASCADE, related_name='GradeScores')
    initial_grades = models.FloatField(null=True, blank=True)
    transmuted_grades = models.FloatField(null=True, blank=True)
    grade_scores = models.JSONField(null=True, blank=True)


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
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    grade = models.CharField(max_length=50)
    section = models.CharField(max_length=50)
    subject = models.CharField(max_length=50, null=True, blank=True)
    final_grade = models.JSONField()

    def __str__(self):
        return f"FinalGrade: {self.student.name} - {self.subject}, Teacher: {self.teacher}"

    def archive(self):
        try:
            with transaction.atomic():
                # Create an instance of ArchivedFinalGrade before deleting the original final grade
                archived_final_grade = ArchivedFinalGrade.objects.create(
                    original_final_grade=self,
                    archived_teacher=self.teacher,
                    archived_student=self.student,
                    archived_grade=self.grade,
                    archived_section=self.section,
                    archived_final_grade=self.final_grade
                )

                # Delete the original final grade instance after archiving
                self.delete()

                # Return the archived final grade instance
                return archived_final_grade
        except Exception as e:
            # Handle exceptions if necessary
            print(f"Error occurred during archiving FinalGrade: {str(e)}")
            return None
    
class ArchivedFinalGrade(models.Model):
    archived_teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    archived_student = models.ForeignKey(ArchivedStudent, on_delete=models.CASCADE)
    archived_grade = models.CharField(max_length=50)
    archived_section = models.CharField(max_length=50)
    archived_final_grade = models.JSONField()

    def __str__(self):
        return f"Archived FinalGrade: {self.archived_student.name} - {self.archived_section}, Teacher: {self.archived_teacher}"
    
    def restore(self):
        try:
            with transaction.atomic():
                # Create a new instance of FinalGrade using archived data
                final_grade = FinalGrade.objects.create(
                    teacher=self.archived_teacher,
                    student=self.archived_student,
                    grade=self.archived_grade,
                    section=self.archived_section,
                    final_grade=self.archived_final_grade
                )

                # Delete the archived final grade instance after restoration
                self.delete()

                # Return the restored FinalGrade instance
                return final_grade
        except Exception as e:
            # Handle exceptions if necessary
            print(f"Error occurred during restoration of ArchivedFinalGrade: {str(e)}")
            return None

class GeneralAverage(models.Model):
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    grade = models.CharField(max_length=50)
    section = models.CharField(max_length=50)
    general_average = models.FloatField(null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.student_name} - {self.grade} - {self.section} - General Average: {self.general_average}"

class QuarterlyGrades(models.Model):

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quarter = models.CharField(max_length=100)
    grades = models.JSONField(null=True)

    def __str__(self):
        return f"{self.student.name}'s grades for {self.quarter}"


    
class ArchivedGeneralAverage(models.Model):
    archived_student = models.ForeignKey(ArchivedStudent, on_delete=models.CASCADE)
    archived_grade = models.CharField(max_length=50)
    archived_section = models.CharField(max_length=50)
    archived_general_average = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Archived General Average: {self.archived_student.name} - {self.archived_grade} - {self.archived_section} - General Average: {self.archived_general_average}"


class ArchivedQuarterlyGrades(models.Model):
    archived_student = models.ForeignKey(ArchivedStudent, on_delete=models.CASCADE)
    archived_quarter = models.CharField(max_length=100)
    archived_grades = models.JSONField(null=True)

    def __str__(self):
        return f"Archived {self.archived_student.name}'s grades for {self.archived_quarter}"




class ProcessedDocument(models.Model):
    document = models.FileField(upload_to='processed_documents/')
    upload_date = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.CASCADE)


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
    def delete(self, *args, **kwargs):
        # Delete associated ProcessedDocument before deleting ExtractedData
        if self.processed_document:
            # Get the file path of the document
            file_path = self.processed_document.document.path
            # Delete the associated file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
            # Delete the ProcessedDocument instance
            self.processed_document.delete()
        super().delete(*args, **kwargs)



class ActivityLog(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    action = models.CharField(max_length=255)
    details = models.TextField()

    def __str__(self):
        return f'{self.user.username} - {self.action}'


class InboxMessage(models.Model):
    to_teacher = models.CharField(max_length=50, null=True, blank=True)
    from_teacher = models.CharField(max_length=50, null=True, blank=True)
    file_name = models.CharField(max_length=50, null=True, blank=True)  
    json_data = models.TextField()
    date_received = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inbox message from {self.from_teacher.username} to {self.to_teacher}"

class AcceptedMessage(models.Model):
    message_id = models.IntegerField(primary_key=True)
    file_name = models.CharField(max_length=255)
    json_data = models.JSONField()
    accepted_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    accepted_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"AcceptedMessage {self.message_id}"

    
class AdvisoryClass(models.Model):
    
    grade = models.CharField(max_length=50, null=True, blank=True)
    section = models.CharField(max_length=50, null=True, blank=True)
    grades_data = models.JSONField(null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, limit_choices_to={'class_type': 'advisory'})

    def set_grades_data(self, data):
        self.grades_data = json.dumps(data)

    def get_grades_data(self):
        return self.grades_data if self.grades_data else {}

    def set_grade_for_subject(self, subject, grades):
        if not self.grades_data:
            self.grades_data = {}
        if subject not in self.grades_data:
            self.grades_data[subject] = {}
        self.grades_data[subject].update(grades)
        
    def get_grade_for_subject(self, subject):
        if self.grades_data and subject in self.grades_data:
            return self.grades_data[subject]
        return None

class ArchivedAdvisoryClass(models.Model):
    grade = models.CharField(max_length=50, null=True, blank=True)
    section = models.CharField(max_length=50, null=True, blank=True)
    grades_data = models.JSONField(null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, limit_choices_to={'class_type': 'advisory'})
    date_archived = models.DateTimeField(auto_now_add=True)  # Record the date when the record was archived

    def set_grades_data(self, data):
        self.grades_data = json.dumps(data)

    def get_grades_data(self):
        return self.grades_data if self.grades_data else {}

    def set_grade_for_subject(self, subject, grades):
        if not self.grades_data:
            self.grades_data = {}
        if subject not in self.grades_data:
            self.grades_data[subject] = {}
        self.grades_data[subject].update(grades)
        
    def get_grade_for_subject(self, subject):
        if self.grades_data and subject in self.grades_data:
            return self.grades_data[subject]
        return None
    
class Announcement(models.Model):

    title = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):

        return self.title
    
class AttendanceRecord(models.Model):

     student = models.ForeignKey(Student, on_delete=models.CASCADE)
     attendance_record = models.JSONField(null=True)

class CoreValues(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)

    def __str__(self):
        return self.name

class BehaviorStatement(models.Model):
    core_value = models.ForeignKey(CoreValues, on_delete=models.CASCADE)
    statement = models.CharField(max_length=255)

    def __str__(self):
        return self.statement

class LearnersObservation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quarter_1 = models.JSONField(null=True)
    quarter_2 = models.JSONField(null=True)
    quarter_3 = models.JSONField(null=True)
    quarter_4 = models.JSONField(null=True)

    def __str__(self):
        return f"LearnersObservation - Student: {self.student}"

class RestoreRequest(models.Model):
    archived_record = models.ForeignKey(ArchivedClassRecord, on_delete=models.CASCADE)
    requester = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    date_requested = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')


class Feedback(models.Model):
    rating = models.CharField(max_length=50, null=True, blank=True)
    feedback_text = models.TextField()

    def __str__(self):
        return f"Rating: {self.rating}, Feedback: {self.feedback_text}"