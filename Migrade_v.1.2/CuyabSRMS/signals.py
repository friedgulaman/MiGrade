from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ClassRecord, Student
from .TeacherViews import calculate_save_final_grades, display_final_grades, display_all_final_grades

@receiver(post_save, sender=ClassRecord)
def calculate_and_save_final_grades(sender, instance, created, **kwargs):
    # Check if it's a new instance or an update
    if created or not instance.pk:
        # New instance (created=True) or instance has no primary key (not saved yet)
        # Retrieve students based on your actual models and logic
        grade = instance.grade
        section = instance.section
        students = Student.objects.filter(grade=grade, section=section)

        # Access the subject directly from the ClassRecord instance
        subject = instance.subject  # Assuming subject is a ForeignKey

        subjects = ClassRecord.objects.filter(grade=grade, section=section, subject=subject).values('subject').distinct()

        # Log a message to check if the signal is triggered
        print(f"Signal triggered for ClassRecord: {instance}")
        print(grade)
        print(section)
        print(subject)
        # Call your calculation function
        # calculate_save_final_grades(grade, section, subject, students, subjects)

        display_final_grades(None, grade, section, subject)
        display_all_final_grades(None, grade, section)
    else:
        # Updated instance
        # You can add logic specific to updates here, if needed
        print(f"ClassRecord instance updated: {instance}")
        grade = instance.grade
        section = instance.section
        students = Student.objects.filter(grade=grade, section=section)

        # Access the subject directly from the ClassRecord instance
        subject = instance.subject  # Assuming subject is a ForeignKey

        subjects = ClassRecord.objects.filter(grade=grade, section=section, subject=subject).values('subject').distinct()

        # Log a message to check if the signal is triggered
        print(f"Signal triggered for ClassRecord: {instance}")
        print(grade)
        print(section)
        print(subject)
        # Call your calculation function
        # calculate_save_final_grades(grade, section, subject, students, subjects)

        display_final_grades(None, grade, section, subject)
        display_all_final_grades(None, grade, section)
