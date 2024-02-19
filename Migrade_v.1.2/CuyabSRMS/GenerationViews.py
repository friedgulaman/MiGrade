from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Student, FinalGrade, GeneralAverage, ClassRecord, Subject, SchoolInformation, QuarterlyGrades
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
    write_sf9_grades,
    write_school_info,

    #SUMMARY OF QUARTERLY
    write_school_info_quarterly,
    write_student_name_quarterly,
    write_quarterly_grade_AP,
    write_quarterly_grade_ENGLISH,

    #FINAL GRADE AND GENERAL AVERAGE
    write_school_info_general_average,
    write_student_name_general_average,
    write_final_grade_ENGLISH,
)
from .models import GradeScores

def generate_summary_of_quarterly_grades(request, grade, section, quarter):
    # Assuming `grade`, `section`, and `quarter` are passed in the URL parameters

    # Query the QuarterlyGrades model
    quarterly_grades_query = QuarterlyGrades.objects.filter(
        quarter=quarter, student__grade=grade, student__section=section,
    )

    school_info = SchoolInformation.objects.all()

    user = request.user
    action = f'{user} generate a Summary of Quarterly Grades ({quarter}) of {grade} {section}'
    details = f'{user} generate a Summary of Quarterly Grades ({quarter}) of {grade} {section} in the system.'
    log_activity(user, action, details)


    print(grade)
    print(section)
    print(quarter)
    # students = [quarterly_grade.student for quarterly_grade in quarterly_grades_query]

    # # Now you can access the students
    # for student in students:
    #     print(student.name)

     # Original file path for SF9 template
        # Original file path
    excel_file_name = "Template - ClassRecord.xlsx"

    # Get the current working directory
    # current_directory = os.getcwd()
    media_directory = os.path.join(settings.MEDIA_ROOT, 'excel-files')
    created_directory = os.path.join(settings.MEDIA_ROOT, 'created-sf9')

    # Generate a timestamp for the copy
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Create the path for the original file
    original_file_path = os.path.join(media_directory, excel_file_name)

    # Create a path for the copied file with a timestamp
    copied_file_path = os.path.join(created_directory, f'SUMMARY OF QUARTERLY GRADES {quarter} {timestamp}.xlsx')

    # Copy the Excel file
    shutil.copyfile(original_file_path, copied_file_path)

    try:
        # Open the copied SF9 Excel file
        workbook = openpyxl.load_workbook(copied_file_path)

            # Select the desired sheet (use the correct sheet name from the output)
        input_sheet_name = 'INPUT DATA'
        input_sheet = workbook[input_sheet_name]

        sheet_name = 'SUMMARY'
        sheet = workbook[sheet_name]
        
        write_school_info_quarterly(input_sheet, school_info, quarterly_grades_query)
        write_student_name_quarterly(input_sheet, quarterly_grades_query)
        write_quarterly_grade_AP(sheet, quarterly_grades_query)
        write_quarterly_grade_ENGLISH(sheet, quarterly_grades_query)

            # Save the changes to the SF9 workbook
        workbook.save(copied_file_path)

            # Create an HTTP response with the updated SF9 Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f'SUMMARY OF QUARTERLY GRADES ({quarter}) {timestamp}.xlsx'
        encoded_filename = urllib.parse.quote(filename)
        response['Content-Disposition'] = f'attachment; filename="{encoded_filename}"'

        with open(copied_file_path, 'rb') as excel_file:
                response.write(excel_file.read())

        return response

    except Exception as e:
        # Handle exceptions, such as a corrupted file
        return HttpResponse(f"An error occurred: {e}")

def generate_final_and_general_grades(request, grade, section):
    # Assuming `grade`, `section`, and `quarter` are passed in the URL parameters

    # Query the QuarterlyGrades model
    general_grades_query = GeneralAverage.objects.filter(
        student__grade=grade, student__section=section,
    )

    final_grades_query = FinalGrade.objects.filter(
        student__grade=grade, student__section=section,
    )

    school_info = SchoolInformation.objects.all()


    user = request.user
    action = f'{user} generate the Summary of Final Grade and General Average of {grade} {section}'
    details = f'{user} generate the Summary of Final Grade and General Average of {grade} {section} in the system.'
    log_activity(user, action, details)


    print(grade)
    print(section)

    # students = [quarterly_grade.student for quarterly_grade in quarterly_grades_query]

    # # Now you can access the students
    # for student in students:
    #     print(student.name)

     # Original file path for SF9 template
        # Original file path
    excel_file_name = "FINAL GRADE.xlsx"

    # Get the current working directory
    # current_directory = os.getcwd()
    media_directory = os.path.join(settings.MEDIA_ROOT, 'excel-files')
    created_directory = os.path.join(settings.MEDIA_ROOT, 'created-sf9')

    # Generate a timestamp for the copy
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Create the path for the original file
    original_file_path = os.path.join(media_directory, excel_file_name)

    # Create a path for the copied file with a timestamp
    copied_file_path = os.path.join(created_directory, f'Final and General Average {grade} {section} {timestamp}.xlsx')

    # Copy the Excel file
    shutil.copyfile(original_file_path, copied_file_path)

    try:
        # Open the copied SF9 Excel file
        workbook = openpyxl.load_workbook(copied_file_path)

            # Select the desired sheet (use the correct sheet name from the output)
        # input_sheet_name = 'INPUT DATA'
        # input_sheet = workbook[input_sheet_name]

        sheet_name = 'SUMMARY - FINAL GRADES'
        sheet = workbook[sheet_name]
        
        write_school_info_general_average(sheet, school_info, general_grades_query)
        write_student_name_general_average(sheet, general_grades_query)
        write_final_grade_ENGLISH(sheet, final_grades_query, general_grades_query)
        # write_quarterly_grade_AP(sheet, quarterly_grades_query)
        # write_quarterly_grade_ENGLISH(sheet, quarterly_grades_query)

            # Save the changes to the SF9 workbook
        workbook.save(copied_file_path)

            # Create an HTTP response with the updated SF9 Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f'Final and General Average {grade} {section} {timestamp}.xlsx'
        encoded_filename = urllib.parse.quote(filename)
        response['Content-Disposition'] = f'attachment; filename="{encoded_filename}"'

        with open(copied_file_path, 'rb') as excel_file:
                response.write(excel_file.read())

        return response

    except Exception as e:
        # Handle exceptions, such as a corrupted file
        return HttpResponse(f"An error occurred: {e}")

def generate_excel_for_grades(request, grade, section, subject, quarter):
    # Get GradeScores for the specified grade, section, and subject
    grade_scores_queryset = GradeScores.objects.filter(class_record__grade=grade,
                                                        class_record__section=section,
                                                        class_record__subject=subject,
                                                        class_record__quarters=quarter)
    school_info = SchoolInformation.objects.all()

    grade_name = grade
    section_name = section
    subject_name = subject
    quarter_name = quarter
    for grade_score in grade_scores_queryset:
        class_record_name = grade_score.class_record.name
        teacher_name = f"{grade_score.class_record.teacher.user.first_name} {grade_score.class_record.teacher.user.last_name}".upper()
        

    user = request.user
    action = f'{user} generate a Class Record name "{class_record_name}"'
    details = f'{user} generate a Class Record named "{class_record_name}" in the system.'
    log_activity(user, action, details)


        # Original file path
    excel_file_name = "TEMPLATE - CLASSRECORD (2).xlsx"

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


        write_school_info(sheet, school_info, grade, section, teacher_name)


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
    
def generate_excel_for_all_subjects(request, grade, section, quarter):
    # Get GradeScores for the specified grade, section, and quarter
    grade_scores_queryset = GradeScores.objects.filter(class_record__grade=grade,
                                                        class_record__section=section,
                                                        class_record__quarters=quarter)
    
    school_info = SchoolInformation.objects.all()
    
    grade_name = grade
    section_name = section
    quarter_name = quarter

    # Logging activity
    user = request.user
    class_record_name = ""  # Initialize class record name
    for grade_score in grade_scores_queryset:
        class_record_name = grade_score.class_record.name

    action = f'{user} generate a Class Record name "{class_record_name}"'
    details = f'{user} generate a Class Record named "{class_record_name}" in the system.'
    log_activity(user, action, details)

    # File paths
    excel_file_name = "Template - ClassRecord.xlsx"
    media_directory = os.path.join(settings.MEDIA_ROOT, 'excel-files')
    created_directory = os.path.join(settings.MEDIA_ROOT, 'created-class-record')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    original_file_path = os.path.join(media_directory, excel_file_name)
    copied_file_path = os.path.join(created_directory, f'ClassRecord_{grade_name}_{section_name}_AllSubjects_{quarter_name}_{timestamp}.xlsx')

    # Copy the Excel file
    shutil.copyfile(original_file_path, copied_file_path)

    try:
        # Open the copied Excel file
        workbook = openpyxl.load_workbook(copied_file_path)

        # Iterate through all sheets in the workbook
        for sheet_name in workbook.sheetnames:
            # Identify the subject based on the sheet name
            sheet = workbook[sheet_name]

            # Write data to the selected sheet
            write_student_names(sheet, grade_scores_queryset)
            write_scores_hps_written(sheet, grade_scores_queryset)
            write_scores_hps_performance(sheet, grade_scores_queryset)
            write_scores_hps_quarterly(sheet, grade_scores_queryset)
            write_written_works_scores(sheet, grade_scores_queryset)
            write_performance_tasks_scores(sheet, grade_scores_queryset)
            write_quarterly_assessment_scores(sheet, grade_scores_queryset)
            write_initial_grade(sheet, grade_scores_queryset)
            write_transmuted_grade(sheet, grade_scores_queryset)
            write_school_info(sheet, school_info)

        # Save changes to the workbook
        workbook.save(copied_file_path)

        # Prepare HTTP response with updated Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=ClassRecord_{grade_name}_{section_name}_AllSubjects_{quarter_name}_{timestamp}.xlsx'

        with open(copied_file_path, 'rb') as excel_file:
            response.write(excel_file.read())

        return response

    except Exception as e:
        # Handle exceptions
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



@login_required
def generate_per_subject_view(request):
    # Retrieve the user and check if the user is a teacher
    user = request.user
    if hasattr(user, 'teacher'):
        # Retrieve the teacher associated with the user
        teacher = user.teacher

        # Filter class records based on the teacher
        class_records = ClassRecord.objects.filter(teacher=teacher)

        # Keep track of unique grade and section combinations
        unique_combinations = set()
        unique_class_records = []

        # Iterate through class records to filter out duplicates
        for record in class_records:
            combination = (record.grade, record.section)
            # Check if the combination is unique
            if combination not in unique_combinations:
                unique_combinations.add(combination)
                unique_class_records.append(record)

        context = {
            'class_records': unique_class_records,
        }

        return render(request, 'teacher_template/adviserTeacher/generate_per_subject.html', context)
    
    else:
        # Handle the case where the user is not a teacher
        return render(request, "teacher_template/adviserTeacher/home_adviser_teacher.html")


@login_required
def generate_per_all_subject_view(request):
    # Retrieve the user and check if the user is a teacher
    user = request.user
    if hasattr(user, 'teacher'):
        # Retrieve the teacher associated with the user
        teacher = user.teacher

        # Filter class records based on the teacher
        class_records = ClassRecord.objects.filter(teacher=teacher)

        # Keep track of unique grade and section combinations
        unique_combinations = set()
        unique_class_records = []

        # Iterate through class records to filter out duplicates
        for record in class_records:
            combination = (record.grade, record.section)
            # Check if the combination is unique
            if combination not in unique_combinations:
                unique_combinations.add(combination)
                unique_class_records.append(record)

        context = {
            'class_records': unique_class_records,
        }

        return render(request, 'teacher_template/adviserTeacher/generate_per_all_subject.html', context)
    
    else:
        # Handle the case where the user is not a teacher
        return render(request, "teacher_template/adviserTeacher/home_adviser_teacher.html")
    
def generate_grade_section_list(request):
    # Assuming the user is logged in
    user = request.user

    # Check if the user is a teacher
    if user.is_authenticated and hasattr(user, 'teacher'):
        # Retrieve the teacher associated with the user
        teacher = user.teacher

        grade = request.GET.get('grade')
        section = request.GET.get('section')
        
        # Filter class records based on the teacher
        class_records = ClassRecord.objects.filter(teacher=teacher, grade=grade, section=section)

        # Fetch distinct subjects based on grade and section
        subjects = Subject.objects.values_list('name', flat=True).distinct()


        context = {
            'grade': grade,
            'section': section,
            'class_records': class_records,
            'subjects': subjects,
        }

        return render(request, 'teacher_template/adviserTeacher/generate_grade_section_list.html', context)
    else:
        # Handle the case where the user is not a teacher
        return render(request, "teacher_template/adviserTeacher/home_adviser_teacher.html")