# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import ClassRecord, Student, GradeScores
# from .TeacherViews import calculate_save_final_grades, display_final_grades, display_all_final_grades

# @receiver(post_save, sender=Class)
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
#         display_all_final_grades(None, grade, section)


from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AdvisoryClass, QuarterlyGrades
from .TeacherViews import grade_summary, get_subject_score

@receiver(post_save, sender=AdvisoryClass)
def update_quarterly_grades(sender, instance, created, **kwargs):
    # Check if the instance is created or updated
    if created or not created:
        # Extract necessary data from the AdvisoryClass instance
        grade = instance.grade
        section = instance.section

        # Retrieve the student(s) associated with the AdvisoryClass
        student = AdvisoryClass.objects.filter(grade=grade, section=section)

        # Extract the quarter information from the first student
        if student.exists():
            # Assuming quarter information is stored within the grades_data field
            first_student = student.first()
            quarter_data = first_student.grades_data.get('quarter')  # Adjust as per your data structure
            if quarter_data:
                quarter = quarter_data.get('quarter_value')  # Adjust the key based on your data
                # Call the grade_summary function with the extracted quarter value
                grade_summary(None, grade, section, quarter)

                # Assuming you want to call get_subject_score for each subject
                # for subject in subjects:
                #     get_subject_score(student, subject, quarter)
            else:
                print("Quarter data not found for the student.")
        else:
            print("No students found for the AdvisoryClass.")