from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Student, FinalGrade, GeneralAverage, ClassRecord
from .views import log_activity
import os
import openpyxl
import pandas as pd
import shutil
from datetime import datetime
import urllib.parse
from django.conf import settings
from .utils import (
    write_student_names,
    write_scores_hps_written,
    write_scores_hps_performance,
    write_scores_hps_quarterly,
    write_written_works_scores,
    write_performance_tasks_scores,
    write_quarterly_assessment_scores,
    write_initial_grade,
    write_transmuted_grade,
    write_sf9_data,
    write_sf9_grades
)


from .models import GradeScores

def generate_excel_for_grades(request, grade, section, subject, quarter):
    # Get GradeScores for the specified grade, section, and subject
    grade_scores_queryset = GradeScores.objects.filter(class_record__grade=grade,
                                                        class_record__section=section,
                                                        class_record__subject=subject,
                                                        class_record__quarters=quarter)
    
    grade_name = grade
    section_name = section
    subject_name = subject
    quarter_name = quarter
    for grade_score in grade_scores_queryset:
        class_record_name = grade_score.class_record.name

    user = request.user
    action = f'{user} generate a Class Record name "{class_record_name}"'
    details = f'{user} generate a Class Record named "{class_record_name}" in the system.'
    log_activity(user, action, details)


        # Original file path
    excel_file_name = "TEMPLATE - SF1.xlsx"

    # Get the current working directory
    # current_directory = os.getcwd()
    media_directory = os.path.join(settings.MEDIA_ROOT, 'excel-files')
    created_directory = os.path.join(settings.MEDIA_ROOT, 'created-class-record')

    # Generate a timestamp for the copy
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Create the path for the original file
    original_file_path = os.path.join(media_directory, excel_file_name)

    # Create a path for the copied file with a timestamp
    copied_file_path = os.path.join(created_directory, f'SF1 {grade_name}_{section_name}_{subject_name}_{quarter_name}_{timestamp}.xlsx')

    # Copy the Excel file
    shutil.copyfile(original_file_path, copied_file_path)

    try:
        # Open the copied Excel file
        workbook = openpyxl.load_workbook(copied_file_path)

        # Select the desired sheet (use the correct sheet name from the output)
        desired_sheet_name = 'Sheet1'
        sheet = workbook[desired_sheet_name]

        # # Write student names
        write_student_names(sheet, grade_scores_queryset)

        # Write scores_hps_written
        write_scores_hps_written(sheet, grade_scores_queryset)

        # Write scores_hps_performance
        write_scores_hps_performance(sheet, grade_scores_queryset)

        # Write scores_hps_quarterly
        write_scores_hps_quarterly(sheet, grade_scores_queryset)

        # Write Written_works_score
        write_written_works_scores(sheet, grade_scores_queryset)

        # Write performance_tasks_score
        write_performance_tasks_scores(sheet, grade_scores_queryset)

        # Write quarterly assessment score
        write_quarterly_assessment_scores(sheet, grade_scores_queryset)

        # Write Initial Grade
        write_initial_grade(sheet, grade_scores_queryset)

        # Write transmuted Grade
        write_transmuted_grade(sheet, grade_scores_queryset)

        # Save the changes to the workbook
        workbook.save(copied_file_path)

        # Create an HTTP response with the updated Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=Class Record {grade_name}_{section_name}_{subject_name}_{quarter_name}_{timestamp}.xlsx'

        with open(copied_file_path, 'rb') as excel_file:
            response.write(excel_file.read())

        return response

    except Exception as e:
        # Handle exceptions, such as a corrupted file
        return HttpResponse(f"An error occurred: {e}")
    

def generate_excel_for_sf9(request, student_id):

    # Retrieve the student object
    student = get_object_or_404(Student, id=student_id)

    final_grade = FinalGrade.objects.filter(student=student).first()

    general_average = GeneralAverage.objects.filter(student=student).first()

    student_name = student.name
    grade_name = student.grade
    section_name = student.section

    user = request.user
    action = f'{user} generated an SF9 for the Student "{student_name} in {grade_name} {section_name}"'
    details = f'{user} generated an SF9 for the Student "{student_name} in {grade_name} {section_name} in the system.'
    log_activity(user, action, details)



    print(student_name)

    # Original file path for SF9 template
        # Original file path
    excel_file_name = "ELEM SF9 (Learner's Progress Report Card).xlsx"

    # Get the current working directory
    # current_directory = os.getcwd()
    media_directory = os.path.join(settings.MEDIA_ROOT, 'excel-files')
    created_directory = os.path.join(settings.MEDIA_ROOT, 'created-sf9')

    # Generate a timestamp for the copy
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Create the path for the original file
    original_file_path = os.path.join(media_directory, excel_file_name)

    # Create a path for the copied file with a timestamp
    copied_file_path = os.path.join(created_directory, f'SF9 {student_name}_{grade_name}_{section_name}_{timestamp}.xlsx')

    # Copy the Excel file
    shutil.copyfile(original_file_path, copied_file_path)

    try:
        # Open the copied SF9 Excel file
        workbook = openpyxl.load_workbook(copied_file_path)

            # Select the desired sheet (use the correct sheet name from the output)
        front_sheet_name = 'FRONT'
        front_sheet = workbook[front_sheet_name]

        back_sheet_name = 'BACK'
        back_sheet = workbook[back_sheet_name]

            # Write SF9-specific data using a utility function (update this function based on your needs)
        write_sf9_data(front_sheet, student)

        write_sf9_grades(back_sheet, final_grade, general_average)

            # Save the changes to the SF9 workbook
        workbook.save(copied_file_path)

            # Create an HTTP response with the updated SF9 Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f'SF9_{student_name}_{grade_name}_{section_name}_{timestamp}.xlsx'
        encoded_filename = urllib.parse.quote(filename)
        response['Content-Disposition'] = f'attachment; filename="{encoded_filename}"'

        with open(copied_file_path, 'rb') as excel_file:
                response.write(excel_file.read())

        return response

    except Exception as e:
        # Handle exceptions, such as a corrupted file
        return HttpResponse(f"An error occurred: {e}")


def generate_per_subject_view(request):
    # Assuming the user is logged in
    user = request.user

    # Check if the user is a teacher
    if user.is_authenticated and hasattr(user, 'teacher'):
        # Retrieve the teacher associated with the user
        teacher = user.teacher

        # Filter class records based on the teacher
        class_records = ClassRecord.objects.filter(teacher=teacher)

        context = {
            'class_records': class_records,
        }
        print(class_records)

        return render(request, 'teacher_template/adviserTeacher/generate_per_subject.html', context)
    
    else:
        # Handle the case where the user is not a teacher
        return render(request, "teacher_template/adviserTeacher/home_adviser_teacher.html")