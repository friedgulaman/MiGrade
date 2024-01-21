from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Student
import os
import openpyxl
import pandas as pd
import shutil
from datetime import datetime
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
    write_sf9_data
)


from .models import GradeScores

def generate_excel_for_grades(request, grade, section, subject):
    # Get GradeScores for the specified grade, section, and subject
    grade_scores_queryset = GradeScores.objects.filter(class_record__grade=grade,
                                                        class_record__section=section,
                                                        class_record__subject=subject)

        # Original file path
    excel_file_name = "TEMPLATE - SF1.xlsx"

    # Get the current working directory
    current_directory = os.getcwd()

    # Generate a timestamp for the copy
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Create the path for the original file
    original_file_path = os.path.join(current_directory, excel_file_name)

    # Create a path for the copied file with a timestamp
    copied_file_path = os.path.join(current_directory, f'TEMPLATE - SF1_copy_{timestamp}.xlsx')

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
        response['Content-Disposition'] = f'attachment; filename=grades_export_{timestamp}.xlsx'

        with open(copied_file_path, 'rb') as excel_file:
            response.write(excel_file.read())

        return response

    except Exception as e:
        # Handle exceptions, such as a corrupted file
        return HttpResponse(f"An error occurred: {e}")
    

def generate_excel_for_sf9(request, student_id):
    # Retrieve the student object
    student = get_object_or_404(Student, id=student_id)

    # Original file path for SF9 template
        # Original file path
    excel_file_name = "ELEM SF9 (Learner's Progress Report Card).xlsx"

    # Get the current working directory
    current_directory = os.getcwd()

    # Generate a timestamp for the copy
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Create the path for the original file
    original_file_path = os.path.join(current_directory, excel_file_name)

    # Create a path for the copied file with a timestamp
    copied_file_path = os.path.join(current_directory, f'SF9{timestamp}.xlsx')

    # Copy the Excel file
    shutil.copyfile(original_file_path, copied_file_path)

    try:
        # Open the copied SF9 Excel file
        workbook = openpyxl.load_workbook(copied_file_path)

        # Select the desired sheet (use the correct sheet name from the output)
        desired_sheet_name = 'FRONT'
        sheet = workbook[desired_sheet_name]

        # Write SF9-specific data using a utility function (update this function based on your needs)
        write_sf9_data(sheet, student)

        # Save the changes to the SF9 workbook
        workbook.save(copied_file_path)

        # Create an HTTP response with the updated SF9 Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=sf9_export_{timestamp}.xlsx'

        with open(copied_file_path, 'rb') as excel_file:
            response.write(excel_file.read())

        return response

    except Exception as e:
        # Handle exceptions, such as a corrupted file
        return HttpResponse(f"An error occurred: {e}")