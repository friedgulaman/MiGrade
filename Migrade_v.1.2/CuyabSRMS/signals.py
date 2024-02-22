# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import ClassRecord, Student, GradeScores
# from .TeacherViews import calculate_save_final_grades, display_final_grades, display_all_final_grades

# @receiver(post_save, sender=Student)
# def calculate_and_save_final_grades(sender, instance, created, **kwargs):
#     # Check if it's a new instance or an update
#     if created or not instance.pk:

#         grade = instance.grade
#         section = instance.section
#         students = Student.objects.filter(grade=grade, section=section)

#         # Access the subject directly from the ClassRecord instance
#         subject = instance.subject  # Assuming subject is a ForeignKey

#         subjects = ClassRecord.objects.filter(grade=grade, section=section, subject=subject).values('subject').distinct()



#         display_final_grades(None, grade, section, subject)
#         # display_all_final_grades(None, grade, section)
#     else:

#         print(f"ClassRecord instance updated: {instance}")
#         grade = instance.grade
#         section = instance.section
#         students = Student.objects.filter(grade=grade, section=section)

#         # Access the subject directly from the ClassRecord instance
#         subject = instance.subject  # Assuming subject is a ForeignKey

#         subjects = ClassRecord.objects.filter(grade=grade, section=section, subject=subject).values('subject').distinct()

#         display_final_grades(None, grade, section, subject)
#         # display_all_final_grades(None, grade, section)
