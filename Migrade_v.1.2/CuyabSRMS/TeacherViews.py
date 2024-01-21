import json
import os

import io
import re

from CuyabSRMS.utils import transmuted_grade
from django import forms
import openpyxl
from django.contrib import messages
from django.shortcuts import render
from .models import Grade, GradeScores, Section, Student, Teacher, Subject, Quarters, ClassRecord, FinalGrade, GeneralAverage
from django.contrib.auth import get_user_model  # Add this import statement
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
import logging
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import IntegrityError
from django.contrib import messages
#OCR
from .forms import DocumentUploadForm
from .models import ProcessedDocument, ExtractedData
from google.cloud import documentai_v1beta3 as documentai
from django.shortcuts import render
from .views import *
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.template.loader import render_to_string

from django.template import RequestContext
#Grade
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.files.uploadedfile import TemporaryUploadedFile


#Grade
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .forms import GradeScoresForm



@login_required
def home_teacher(request):
    return render(request, 'teacher_template/home_teacher.html')
@login_required
def upload_adviser_teacher(request):
    return render(request, 'teacher_template/adviserTeacher/upload.html')
@login_required
def new_classrecord(request):
        return render(request, 'teacher_template/adviserTeacher/new_classrecord.html')
@login_required
def classes(request):
        return render(request, 'teacher_template/adviserTeacher/classes.html')


# adviser
@login_required
def home_adviser_teacher(request):
    return render(request, 'teacher_template/adviserTeacher/home_adviser_teacher.html')

@login_required
def dashboard(request):
     # Get the currently logged-in teacher
    teacher = request.user.teacher

    # Retrieve the related section
    section = teacher.sections.first()  # Assuming a teacher can have multiple sections

    if section:
        # Get the grade from the related section
        grade = section.grade
    else:
        # Handle the case where no section is related to the teacher
        grade = None

    # Filter students based on the teacher's ID
    students = Student.objects.filter(teacher=teacher)

    # Count the number of students
    num_students = students.count()

    # Count the number of male (M) and female (F) students
    num_male_students = students.filter(sex='M').count()
    num_female_students = students.filter(sex='F').count()

    context = {
        'num_students': num_students,
        'grade': grade,  # Include the grade in the context
        'section': section,
        'num_male_students': num_male_students,
        'num_female_students': num_female_students,
    }
    return render(request, 'teacher_template/home_teacher.html', context)

# Your combined view
def process_google_sheet(spreadsheet_id, sheet_name):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'keys.json'

    creds = None
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    lrn_data = None

    try:
        service = build('sheets', 'v4', credentials=creds)

        def get_sheet_values(spreadsheet_id, start_range, end_range):
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,  # Use the provided spreadsheet_id
                range=f"{start_range}:{end_range}",  # Correct the range format
            ).execute()
            values = result.get('values', [])
            print(values)
            return values
        
        def find_lrn_and_store_as_dict(sheet_values):
            lrn_row_index = None
            lrn_col_index = None
            lrn_data = {}

            for i, row in enumerate(sheet_values):
                if "LRN" in row:
                    lrn_row_index = i
                    lrn_col_index = row.index("LRN")
                    break

            if lrn_row_index is not None:
                current_lrn = None

                for i in range(lrn_row_index + 1, len(sheet_values)):
                    row = sheet_values[i]
                    if lrn_col_index < len(row):
                        lrn_value = row[lrn_col_index]
                        if len(lrn_value) == 12 and lrn_value.isdigit():
                            current_lrn = lrn_value
                            lrn_data[current_lrn] = []
                        else:
                            current_lrn = None

                    if current_lrn:
                        non_empty_fields = [field for field in row if field.strip() != '']
                        lrn_data[current_lrn].append(non_empty_fields)

            return lrn_data
        
        print(lrn_data)

        existing_sheet_name = sheet_name
        existing_sheet_values = get_sheet_values(spreadsheet_id, "A1", "ZZ1000")

        if existing_sheet_values:
            lrn_data = find_lrn_and_store_as_dict(existing_sheet_values)
            

        return lrn_data

    except Exception as e:
        logging.error(f"An error occurred while processing the Google Sheet: {str(e)}")
        return None  # Return None or handle the error as needed


def get_sections(request):
    grade_id = request.GET.get('grade_id')
    
    # Query your database to get sections for the selected grade
    sections = Section.objects.filter(grade_id=grade_id)

    # Serialize the sections into a JSON response
    sections_data = [{'id': section.id, 'name': section.name} for section in sections]

    return JsonResponse({'sections': sections_data})

def get_sheet_values(sheet, start_range, end_range):
    values = []
    for row in sheet.iter_rows(min_row=start_range[0], min_col=start_range[1], max_row=end_range[0], max_col=end_range[1]):
        row_values = [cell.value for cell in row]
        values.append(row_values)
    return values

def find_lrn_and_store_as_dict(sheet_values):
    lrn_row_index = None
    lrn_col_index = None
    lrn_data = {}  # Initialize an empty dictionary to store LRN data

    for i, row in enumerate(sheet_values):
        if "LRN" in row:
            lrn_row_index = i
            lrn_col_index = row.index("LRN")
            break

    if lrn_row_index is not None:
        current_lrn = None

        for i in range(lrn_row_index + 1, len(sheet_values)):
            row = sheet_values[i]
            if lrn_col_index < len(row):
                lrn_value = row[lrn_col_index]
                if len(str(lrn_value)) == 12 and str(lrn_value).isdigit():
                    current_lrn = lrn_value
                    lrn_data[current_lrn] = []  # Initialize an empty list for the LRN
                else:
                    current_lrn = None  # Reset current LRN if it's not 12 digits

                if current_lrn:
                    non_empty_fields = [field for field in row if field is not None and str(field).strip() != '']
                    lrn_data[current_lrn].append(non_empty_fields)  # Append non-empty fields to the LRN

        return lrn_data
    else:
        print("Cell containing 'LRN' not found in the sheet.")
        return lrn_data  # Return an empty dictionary if no LRN cell is found

def upload(request):
    if request.method == 'POST':
        google_sheet_link = request.POST.get('google_sheet_link')
        excel_file = request.FILES.get('excel_file')

        if google_sheet_link:
            # Process Google Sheet
            spreadsheet_id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', google_sheet_link)

            if spreadsheet_id_match:
                spreadsheet_id = spreadsheet_id_match.group(1)
                sheet_name_match = re.search(r'#gid=([0-9]+)', google_sheet_link)
                sheet_name = sheet_name_match.group(1) if sheet_name_match else None

                lrn_data = process_google_sheet(spreadsheet_id, sheet_name)

                if lrn_data is not None:
                    return render(request, 'teacher_template/adviserTeacher/upload.html', {
                        'lrn_data': lrn_data,
                    })
                else:
                    messages.error(request, "Failed to process the Google Sheet")
            else:
                messages.error(request, "Invalid Google Sheet link")

        elif excel_file:
            # Check if the file has a valid Excel extension
            valid_excel_extensions = ['.xls', '.xlsx']
            file_extension = os.path.splitext(excel_file.name)[1].lower()

            if file_extension not in valid_excel_extensions:
                messages.error(request, "Invalid Excel file. Please upload a valid Excel file.")
                return render(request, 'teacher_template/adviserTeacher/upload.html')

            # Save the uploaded Excel file temporarily
            temp_file_path = 'temp.xlsx'
            with open(temp_file_path, 'wb') as temp_file:
                for chunk in excel_file.chunks():
                    temp_file.write(chunk)

            # Load the Excel workbook
            try:
                workbook = openpyxl.load_workbook(temp_file_path)
            except Exception as e:
                os.remove(temp_file_path)  # Remove temporary file
                messages.error(request, f"Failed to load the Excel File: {str(e)}")
                return render(request, 'teacher_template/adviserTeacher/upload.html')

            # Get the values from the existing sheet
            try:
                existing_sheet_name = workbook.sheetnames[0]  # Use the first sheet
                existing_sheet = workbook[existing_sheet_name]
            except KeyError as e:
                os.remove(temp_file_path)  # Remove temporary file
                messages.error(request, f"Worksheet '{existing_sheet_name}' does not exist in the Excel File")
                return render(request, 'teacher_template/adviserTeacher/upload.html')

            existing_sheet_values = get_sheet_values(existing_sheet, (1, 1), (existing_sheet.max_row, existing_sheet.max_column))

            if existing_sheet_values:
                lrn_data = find_lrn_and_store_as_dict(existing_sheet_values)
                return render(request, 'teacher_template/adviserTeacher/upload.html', {
                    'lrn_data': lrn_data,
                })
            else:
                os.remove(temp_file_path)  # Remove temporary file
                messages.error(request, "Failed to process the Excel File")
        else:
            messages.error(request, "Invalid Excel File")
            
    return render(request, 'teacher_template/adviserTeacher/upload.html')

@csrf_exempt
@login_required
def save_json_data(request):
    if request.method == 'POST':
        if not hasattr(request.user, 'teacher'):
            response_data = {'message': 'User is not a teacher.'}
            return JsonResponse(response_data, status=403)

        try:
            received_data = json.loads(request.body)
            teacher = request.user.teacher  # Get the currently logged-in teacher

            # Get the selected grade and section from the request data
            selected_grade = received_data.get('selectedGrade', '')
            selected_section = received_data.get('selectedSection', '')

            # Update the Grade and Section tables with teacher ID
            teacher.grade = selected_grade
            teacher.section = selected_section
            teacher.save()

            for item in received_data['rows']:
                lrn = item.get('LRN')
                name = item.get('Name')
                sex = item.get('Sex')
                birthday = item.get('Birthday')

                # Create or update the Student object based on LRN
                student, created = Student.objects.get_or_create(
                    lrn=lrn,
                    defaults={
                        'name': name,
                        'sex': sex,
                        'birthday': birthday,
                        'teacher': teacher,
                        'grade': selected_grade,
                        'section': selected_section,
                    }
                )

                # Update other fields if needed
                student.name = name
                student.sex = sex
                student.birthday = birthday
                # Update other fields as necessary

                student.save()

                # Update the 'teacher' field in the 'Section' model
                section = Section.objects.get(name=selected_section, grade__name=selected_grade)
                section.teacher = teacher
                section.save()

            response_data = {'message': 'JSON data saved successfully'}
            return JsonResponse(response_data)
        except json.JSONDecodeError:
            response_data = {'message': 'Invalid JSON data'}
            return JsonResponse(response_data, status=400)
    else:
        response_data = {'message': 'Method not allowed'}
        return JsonResponse(response_data, status=405)


def get_grades_and_sections(request):
    teacher = get_object_or_404(Teacher, user=request.user)  # Assuming you have a User associated with Teacher

    # Retrieve a list of grades and sections that have the specific teacher
    grades = Grade.objects.filter(sections__teacher=teacher).distinct().values('id', 'name')
    sections = Section.objects.filter(teacher=teacher).values('id', 'name')

    # Convert the grades and sections to a dictionary
    data = {
        'grades': list(grades),
        'sections': list(sections),
    }

    return JsonResponse(data)


def class_record(request):
    return render(request, 'teacher_template/adviserTeacher/class_record.html')


def get_grade_details(request):

    user = request.user

    teacher = Teacher.objects.get(user=user)
    grades = Student.objects.values_list('grade', flat=True).distinct()
    sections = Student.objects.values_list('section', flat=True).distinct()
    subjects = Subject.objects.values_list('name', flat=True).distinct()
    quarters = Quarters.objects.values_list('quarters', flat=True).distinct()
    



    context = {
        'teacher': teacher,
        'grades': grades,
        'sections': sections,
        'subjects': subjects,
        'quarters': quarters
    }
    # print("Distinct grades:", grades)
    # print("Distinct sections:", sections)
    # print("Distinct subjects:", subjects)

    return render(request, 'teacher_template/adviserTeacher/new_classrecord.html', context)
   # Replace with the actual URL of your new_classrecord.html

# views.py
def get_students_by_grade_and_section(request):
    if request.method == "POST":
        try:
            grade_name = request.POST.get("grade")
            section_name = request.POST.get("section")
            subject_name = request.POST.get("subject")
            quarter_name = request.POST.get("quarter")

            user = request.user
            teacher = get_object_or_404(Teacher, user=user)

            # Use a more unique identifier for the class record name
            classrecord_name = f'{grade_name}{section_name}{subject_name}{quarter_name}{teacher.id}'

            classrecord = ClassRecord(
                name=classrecord_name,
                grade=grade_name,
                section=section_name,
                subject=subject_name,
                quarters=quarter_name,
                teacher=teacher,
            )

            classrecord.save()

            # Query the database to retrieve students based on the selected grade and section
            students = Student.objects.filter(grade=grade_name, section=section_name)

            subject = Subject.objects.get(name=subject_name)


            weighted_written_works_percentage = subject.written_works_percentage
            weighted_performance_task_percentage = subject.performance_task_percentage
            weighted_quarterly_assessment_percentage = subject.quarterly_assessment_percentage 


            # Create a dictionary to store scores for each student
            student_scores = {}

            # Loop through the students and retrieve their scores
            for student in students:
                # Assuming you have a field to store the student's name in the Student model
                student_name = student.name

                # Query the database to retrieve the scores for the current student
                # You should modify this query based on your data model
                scores = GradeScores.objects.filter(student=student)

                # Store the scores in the dictionary with the student's name as the key
                student_scores[student_name] = scores

            context = {
                'students': students,
                'subject_name': subject_name,
                'quarters': quarter_name,
                'grade_name': grade_name,
                'section_name': section_name,
                'student_scores': student_scores,
                'written_works_percentage': weighted_written_works_percentage,
                'performance_task_percentage': weighted_performance_task_percentage,
                'quarterly_assessment_percentage': weighted_quarterly_assessment_percentage,
            }

            return render(request, 'teacher_template/adviserTeacher/class_record.html', context)
        
        except IntegrityError as e:
            error_message = 'Duplicate entry. The record already exists.'
            messages.error(request, error_message)
            messages.info(request, 'You are being redirected back to the previous page.')
            return redirect('get_grade_details')

    
    return render(request, 'teacher_template/adviserTeacher/home_adviser_teacher.html')


def calculate_grades(request):
    if request.method == "POST":
        # print(request.POST)
        grade_name = request.POST.get("hidden_grade")
        section_name = request.POST.get("hidden_section")
        subject_name = request.POST.get("hidden_subject")
        quarters_name = request.POST.get("hidden_quarter")
        print(request.POST)
        print(grade_name)
        print(section_name)

        scores_ww_hps = [request.POST.get(f"max_written_works_{i}") for i in range(1, 11)]
        scores_pt_hps = [request.POST.get(f"max_performance_task_{i}") for i in range(1, 11)]
        total_ww_hps = request.POST.get("total_max_written_works")
        total_pt_hps = request.POST.get("total_max_performance_task")
        total_qa_hps = request.POST.get("total_max_quarterly") or 0
        weight_written= request.POST.get("written_works_weight")
        weight_performance= request.POST.get("performance_task_weight")
        weight_quarterly= request.POST.get("quarterly_assessment_weight")

        print(scores_pt_hps)
        print(scores_ww_hps)
        print(total_ww_hps)
        print(total_pt_hps)
        print(total_qa_hps)

        class_record = ClassRecord.objects.get(grade=grade_name, section=section_name, subject=subject_name, quarters=quarters_name)
        # subject_name = request.POST.get("subject")
        # quarter_name = request.POST.get("quarter")
        

        students = Student.objects.filter(grade=grade_name, section=section_name)
        
        for student in students:
            scores_written_works = []
            scores_performance_task = []

            total_score_written = 0
            total_max_score_written = 0
            total_score_performance = 0
            total_max_score_performance = 0
            total_score_quarterly = 0
            total_max_score_quarterly = 0

            weight_input_written = 0
            weight_input_performance = 0
            weight_input_quarterly = 0

            for i in range(1, 11):
                # Retrieve scores and maximum scores for each component
                written_works = request.POST.get(f"scores_written_{student.id}_{i}")
                max_written_works = request.POST.get(f"max_written_works_{i}" )  # Change this to the actual maximum score
                performance_task = request.POST.get(f"scores_performance_task_{student.id}_{i}" )
                max_performance_task = request.POST.get(f"max_performance_task_{i}")  # Change this to the actual maximum score
                # quarterly_assessment = request.POST.get(f"scores_quarterly_assessment_{student.id}_{i}", "0")
                # max_quarterly_assessment = request.POST.get(f"max_quarterly_assessment_{i}", "0")  # Change this to the actual maximum score
                
                # Retrieve weights for each component
                weight_input_written = float(request.POST.get(f"written_works_weight", ))  # Change this to the actual weight for written works
                weight_input_performance = float(request.POST.get(f"performance_task_weight" ))  # Change this to the actual weight for performance tasks
                # weight_input_quarterly = float(request.POST.get(f"weight_quarterly_assessment_{i}", "0"))  # Change this to the actual weight for quarterly assessments
                
                scores_written_works.append(float(written_works) if written_works.isnumeric() else "")
                scores_performance_task.append(float(performance_task) if performance_task.isnumeric() else "")
                # scores_quarterly_assessment.append(float(quarterly_assessment) if quarterly_assessment.isnumeric() else 0)
                total_score_written += float(written_works) if written_works.isnumeric() else 0
                total_max_score_written += float(max_written_works) if max_written_works.isnumeric() else 0
                total_score_performance += float(performance_task) if performance_task.isnumeric() else 0
                total_max_score_performance += float(max_performance_task) if max_performance_task.isnumeric() else 0

                # total_score_quarterly += float(quarterly_assessment) if quarterly_assessment.isnumeric() else 0
                # total_max_score_quarterly += float(max_quarterly_assessment) if max_quarterly_assessment.isnumeric() else 0

            # Perform your calculations (as in your original code)

            quarterly_assessment = request.POST.get(f"qa_total_{student.id}")
            max_quarterly_assessment = request.POST.get(f"total_max_quarterly")  # Change this to the actual maximum score
                
            weight_input_quarterly = float(request.POST.get(f"quarterly_assessment_weight"))  # Change this to the actual weight for quarterly assessments
            total_score_quarterly += float(quarterly_assessment) if quarterly_assessment.isnumeric() else 0
            total_max_score_quarterly += float(max_quarterly_assessment) if max_quarterly_assessment.isnumeric() else 0

            if total_max_score_written > 0:
                percentage_score_written = round((total_score_written / total_max_score_written) * 100, 2)
            else:
                 percentage_score_written = None if total_max_score_written == 0 else 0

            if total_max_score_performance > 0:
               percentage_score_performance = round((total_score_performance / total_max_score_performance) * 100, 2)
            else:
                 percentage_score_performance = None if total_max_score_performance == 0 else 0

            if total_max_score_quarterly > 0:
               percentage_score_quarterly = round((total_score_quarterly / total_max_score_quarterly) * 100, 2)
            else:
                percentage_score_quarterly = None if total_max_score_quarterly == 0 else 0

            weight_written = float(weight_input_written)
            weight_performance = float(weight_input_performance)
            weight_quarterly = float(weight_input_quarterly)

            weighted_score_written = (percentage_score_written / 100) * weight_written if percentage_score_written is not None else None
            weighted_score_performance = (percentage_score_performance / 100) * weight_performance if percentage_score_performance is not None else None
            weighted_score_quarterly = (percentage_score_quarterly / 100) * weight_quarterly if percentage_score_quarterly is not None else None

            rounded_weighted_score_written = round(weighted_score_written, 2) if weighted_score_written is not None else None
            rounded_weighted_score_performance = round(weighted_score_performance, 2) if weighted_score_performance is not None else None
            rounded_weighted_score_quarterly = round(weighted_score_quarterly, 2) if weighted_score_quarterly is not None else None

            if weighted_score_written is not None and weighted_score_performance is not None and weighted_score_quarterly is not None:
                initial_grades = weighted_score_written + weighted_score_performance + weighted_score_quarterly
            else:
                initial_grades = None
            transmuted_grades = transmuted_grade(initial_grades)

            if total_max_score_written > 0 or total_max_score_performance > 0 or total_max_score_quarterly > 0:
                initial_grades = weighted_score_written + weighted_score_performance + weighted_score_quarterly
                transmuted_grades = transmuted_grade(initial_grades)

                # Rounding only if the value is not empty
                rounded_initial_grades = round(initial_grades, 2) if initial_grades != "" else ""
                rounded_transmuted_grades = round(transmuted_grades, 2) if transmuted_grades != "" else ""
            else:
                rounded_initial_grades = None
                rounded_transmuted_grades = None

            # Create a new GradeScores object and populate its fields
            grade_scores = GradeScores(
                student=student,
                class_record=class_record,
                scores_hps_written=scores_ww_hps,
                scores_hps_performance=scores_pt_hps,
                total_ww_hps=total_ww_hps,
                total_qa_hps=total_qa_hps,
                total_pt_hps=total_pt_hps,
                written_works_scores=scores_written_works,
                performance_task_scores=scores_performance_task,
                initial_grades= rounded_initial_grades,
                transmuted_grades= rounded_transmuted_grades,
                total_score_written=total_score_written,
                total_max_score_written=total_max_score_written,
                total_score_performance=total_score_performance,
                total_max_score_performance=total_max_score_performance,
                total_score_quarterly=total_score_quarterly,
                total_max_score_quarterly=total_max_score_quarterly,
                percentage_score_written=percentage_score_written,
                percentage_score_performance=percentage_score_performance,
                percentage_score_quarterly=percentage_score_quarterly,
                weighted_score_written=rounded_weighted_score_written,
                weighted_score_performance=rounded_weighted_score_performance,
                weighted_score_quarterly=rounded_weighted_score_quarterly,
                weight_input_written=weight_input_written,
                weight_input_performance=weight_input_performance,
                weight_input_quarterly=weight_input_quarterly
            )

            # Save the GradeScores object to the database
            grade_scores.save()

            # grade_scores = GradeScores.objects.filter(grade=grade_name, section=section_name)

            # context = {

            #     'grade_scores': grade_scores
            # }

            # return render(request, "teacher_template/adviserTeacher/display_classrecord.html", context)

        # Redirect to a success page or render a response as needed
        # return redirect('display_classrecord')
        return redirect('display_classrecord', class_record_id=class_record.id)

    return render(request, "teacher_template/adviserTeacher/home_adviser_teacher.html")

def display_classrecord(request, class_record_id=None):
    # If class_record_id is provided, retrieve the ClassRecord object
    class_record = get_object_or_404(ClassRecord, id=class_record_id)

    # If class_record_id is not provided, you may want to handle this case differently
    # For example, you can provide a list of available ClassRecord objects for the user to choose from

    # Filter the GradeScores based on the retrieved ClassRecord object
    grade_scores = GradeScores.objects.filter(class_record=class_record)

    context = {
        'class_record': class_record,
        'grade_scores': grade_scores,
    }

    return render(request, 'teacher_template/adviserTeacher/display_classrecord.html', context)
    
def view_classrecord(request):
    
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

        return render(request, 'teacher_template/adviserTeacher/view_classrecord.html', context)
    
    else:
        # Handle the case where the user is not a teacher
        return render(request, "teacher_template/adviserTeacher/home_adviser_teacher.html")
    

@login_required
def display_students(request):
    user = request.user

    if user.user_type == 2:
        teacher = get_object_or_404(Teacher, user=user)
        students = Student.objects.filter(teacher=teacher)
        

        unique_combinations = students.values('grade', 'section').distinct()

        context = {
            'teacher': teacher,
            'unique_grades_sections': unique_combinations,
        }
        return render(request, 'teacher_template/adviserTeacher/classes.html', context)

    return render(request, 'teacher_template/adviserTeacher/classes.html')


def student_list_for_class(request):
    # Assuming the user is logged in
    user = request.user

    # Check if the user is a teacher
    if user.is_authenticated and hasattr(user, 'teacher'):
        # Retrieve the teacher associated with the user
        teacher = user.teacher

        # Filter class records based on the teacher
        class_records = ClassRecord.objects.filter(teacher=teacher)

        grade = request.GET.get('grade')
        section = request.GET.get('section')
        
        # Fetch students based on grade and section
        students = Student.objects.filter(grade=grade, section=section)

        # Fetch distinct subjects based on grade and section
        subjects = ClassRecord.objects.filter(grade=grade, section=section).values('subject').distinct()

        ranked_students = (
            GradeScores.objects
            .filter(class_record__grade=grade, class_record__section=section)
            .order_by('initial_grades')  # Order by initial grades in descending order
            .values('student__id', 'student__name', 'initial_grades')
        )

    context = {
        'grade': grade,
        'section': section,
        'students': students,
        'class_records': class_records,
        'subjects': subjects,
        'ranked_students': ranked_students,
        
    }

    return render(request, 'teacher_template/adviserTeacher/student_list.html', context)


def edit_record(request, record_id):
    # Retrieve the specific record based on the record_id
    record = GradeScores.objects.get(pk=record_id)

    if request.method == 'POST':
        form = GradeScoresForm(request.POST, instance=record)
        if form.is_valid():
            # Save the updated form data to the database
            form.save()
            # Redirect to the same page or another page after successful update
            return redirect('edit_record', record_id=record_id)
    else:
        form = GradeScoresForm(instance=record)

    context = {
        'form': form,
        'record': record,
    }

    return render(request, 'teacher_template/adviserTeacher/edit_records.html', context)


def display_quarterly_summary(request, grade, section, subject, class_record_id):
    # Retrieve the specific class record based on the provided class_record_id
    class_record = get_object_or_404(ClassRecord, id=class_record_id, grade=grade, section=section, subject=subject)

    # Retrieve grade scores related to the class record
    grade_scores = GradeScores.objects.filter(class_record=class_record)

    
    context = {
        'class_record': class_record,
        'grade_scores': grade_scores,
    }

    return render(request, "teacher_template/adviserTeacher/summary_of_quarterly_grade.html", context)


def grade_summary(request, grade, section, quarter):
    students = FinalGrade.objects.filter(grade=grade, section=section)

    # Dictionary to store subject-wise grades for each student
    subject_grades = {}
    print(grade)
    print(section)
    print(quarter)
    quarter_mapping = {
        '1st Quarter': 'quarter1',
        '2nd Quarter': 'quarter2',
        '3rd Quarter': 'quarter3',
        '4th Quarter': 'quarter4',
    }

    # Fetch subject-wise grades for each student
    for student in students:
        subjects = get_subjects(student)
        print(subjects)
        subject_grades[student.student_name] = {}
        for subject in subjects:
            # Map the quarter name to the corresponding column name in the database
            db_quarter = quarter_mapping.get(quarter, quarter)
            subject_grades[student.student_name][subject] = get_subject_score(student, subject, db_quarter)
            print(get_subject_score(student, subject, db_quarter))

    # Move the 'subjects' initialization outside the loop
    subjects = get_subjects(student) if students else []
    
    context = {
        'students': students,
        'subject_grades': subject_grades,
        'subjects': subjects,
        'quarter': quarter,
    }

    return render(request, 'teacher_template/adviserTeacher/quarterly_summary.html', context)



def get_subject_score(student, subject, quarter):
    try:
        grade_instance = FinalGrade.objects.get(
            student_name=student.student_name,  # Update this line
            grade=student.grade,
            section=student.section,
            subject=subject,
        )
        return getattr(grade_instance, quarter, None)
    except FinalGrade.DoesNotExist:
        return None
    
def get_subjects(student):
    # Fetch unique subjects for the given student from the GradeScores model
    subjects = GradeScores.objects.filter(
        class_record__grade=student.grade,
        class_record__section=student.section,
        student__name=student.student_name
    ).values_list('class_record__subject', flat=True).distinct()

    return [subject for subject in subjects if subject]

# def get_subject_grade(student, subject, quarter):
#     # You need to adjust this function based on your actual model relationships and fields
#     grade_score = GradeScores.objects.filter(
#         class_record__grade=student.grade,
#         class_record__section=student.section,
#         class_record__subject=subject,
#         class_record__quarters=quarter,
#         student_name=student.student_name
#     ).first()

#     return getattr(grade_score, f'total_score_{subject.lower()}') if grade_score else None

def calculate_save_final_grades(grade, section, subject, students, subjects):
    quarters = ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter']

    for student in students:
        for subject in subjects:
            subject_name = subject['subject']
            subject_info = {'name': subject_name, 'quarter_grades': {}, 'final_grade': 0}

            # Retrieve initial grades per quarter
            for quarter in quarters:
                grade_score = GradeScores.objects.filter(
                    class_record__grade=grade,
                    class_record__section=section,
                    class_record__subject=subject_name,
                    class_record__quarters=quarter,
                    student__name=student.name
                ).first()

                subject_info['quarter_grades'][quarter] = grade_score.initial_grades if grade_score else 0

            # Get the teacher's name from the ClassRecord
            class_record = ClassRecord.objects.filter(
                grade=grade,
                section=section,
                subject=subject_name
            ).first()

            # Ensure that the class_record and its teacher exist
            if class_record and class_record.teacher:
                subject_info['teacher_name'] = f"{class_record.teacher.user.first_name} {class_record.teacher.user.last_name}"
            else:
                subject_info['teacher_name'] = "Unknown Teacher"

            # Calculate the final grade for the subject
            quarter_grades_values = subject_info['quarter_grades'].values()

            # Convert filtered values to a list before calculating the sum and length
            filtered_values = list(filter(lambda x: x is not None, quarter_grades_values))

            subject_info['final_grade'] = sum(filtered_values) / len(filtered_values) \
                if filtered_values else 0
            
            # Check if a record already exists in the FinalGrade model
            existing_final_grade = FinalGrade.objects.filter(
                teacher=class_record.teacher,
                student_name=student.name,
                grade=grade,
                section=section,
                subject=subject_name
            ).first()

            if existing_final_grade:
                # Update existing record
                existing_final_grade.quarter1 = round(subject_info['quarter_grades']['1st Quarter'] or 0, 2)
                existing_final_grade.quarter2 = round(subject_info['quarter_grades']['2nd Quarter'] or 0, 2)
                existing_final_grade.quarter3 = round(subject_info['quarter_grades']['3rd Quarter'] or 0, 2)
                existing_final_grade.quarter4 = round(subject_info['quarter_grades']['4th Quarter'] or 0, 2)
                existing_final_grade.final_grade = round(subject_info['final_grade'] or 0, 2)
                existing_final_grade.save()
            else:
                # Insert new record
                final_grade = FinalGrade(
                    teacher=class_record.teacher,
                    student_name=student.name,
                    grade=grade,
                    section=section,
                    subject=subject_name,
                    quarter1=round(subject_info['quarter_grades']['1st Quarter'] or 0, 2),
                    quarter2=round(subject_info['quarter_grades']['2nd Quarter'] or 0, 2),
                    quarter3=round(subject_info['quarter_grades']['3rd Quarter'] or 0, 2),
                    quarter4=round(subject_info['quarter_grades']['4th Quarter'] or 0, 2),
                    final_grade=round(subject_info['final_grade'] or 0, 2)
                )
                final_grade.save()



def display_final_grades(request, grade, section, subject):
    students = Student.objects.filter(grade=grade, section=section)
    # Filter subjects to only include the specified subject
    subjects = ClassRecord.objects.filter(grade=grade, section=section, subject=subject).values('subject').distinct()

    calculate_save_final_grades(grade, section, subject, students, subjects)

    final_grades = []
    for student in students:
        student_data = {'id': student.id, 'name': student.name, 'grade': grade, 'section': section, 'subjects': []}

        for subject in subjects:
            subject_name = subject['subject']
            subject_info = {'name': subject_name, 'quarter_grades': {}, 'final_grade': 0}

            # Retrieve final grades from the FinalGrade model
            final_grade = FinalGrade.objects.filter(
                teacher__classrecord__grade=grade,
                teacher__classrecord__section=section,
                student_name=student.name,  # Assuming 'student' is the correct field name
                subject=subject_name
            ).first()   

            if final_grade:
                subject_info['quarter_grades']['1st Quarter'] = final_grade.quarter1
                subject_info['quarter_grades']['2nd Quarter'] = final_grade.quarter2
                subject_info['quarter_grades']['3rd Quarter'] = final_grade.quarter3
                subject_info['quarter_grades']['4th Quarter'] = final_grade.quarter4
                subject_info['final_grade'] = final_grade.final_grade

            # Get the teacher's name from the ClassRecord
            class_record = ClassRecord.objects.filter(
                grade=grade,
                section=section,
                subject=subject_name
            ).first()

            # Ensure that the class_record and its teacher exist
            if class_record and class_record.teacher:
                subject_info['teacher_name'] = f"{class_record.teacher.user.first_name} {class_record.teacher.user.last_name}"
            else:
                subject_info['teacher_name'] = "Unknown Teacher"

            student_data['subjects'].append(subject_info)

        # Append student data to the final grades
        final_grades.append(student_data)

    context = {
        'grade': grade,
        'section': section,
        'final_grades': final_grades,
    }

    return render(request, "teacher_template/adviserTeacher/final_grades.html", context)

def save_general_average(student_data, grade, section):
    # Check if 'general_average' key is present in student_data and is not None
    if 'general_average' in student_data and student_data['general_average'] is not None:
        # Extract relevant information from student_data
        student_name = student_data['name']
        general_average = round(student_data['general_average'], 2)

        # Create or get the GeneralAverage object for the student
        general_average_record, created = GeneralAverage.objects.get_or_create(
            student_name=student_name,
            grade=grade,
            section=section,
        )

        # Set the general_average value and save the record
        general_average_record.general_average = general_average
        general_average_record.save()

def display_all_final_grades(request, grade, section):
    students = Student.objects.filter(grade=grade, section=section)
    # Fetch all distinct subjects for the specified grade and section
    subjects = ClassRecord.objects.filter(grade=grade, section=section).values('subject').distinct()

    final_grades = []
    for student in students:
        student_data = {'id': student.id, 'name': student.name, 'grade': grade, 'section': section, 'subjects': []}

        for subject in subjects:
            subject_name = subject['subject']
            subject_info = {'name': subject_name, 'quarter_grades': {}, 'final_grade': 0}

            # Retrieve final grades from the FinalGrade model
            final_grade = FinalGrade.objects.filter(
                teacher__classrecord__grade=grade,
                teacher__classrecord__section=section,
                student_name=student.name,
                subject=subject_name
            ).first()

            if final_grade:
                subject_info['quarter_grades']['1st Quarter'] = final_grade.quarter1
                subject_info['quarter_grades']['2nd Quarter'] = final_grade.quarter2
                subject_info['quarter_grades']['3rd Quarter'] = final_grade.quarter3
                subject_info['quarter_grades']['4th Quarter'] = final_grade.quarter4
                subject_info['final_grade'] = final_grade.final_grade

            # Get the teacher's name from the ClassRecord
            class_record = ClassRecord.objects.filter(
                grade=grade,
                section=section,
                subject=subject_name
            ).first()

            # Ensure that the class_record and its teacher exist
            if class_record and class_record.teacher:
                subject_info['teacher_name'] = f"{class_record.teacher.user.first_name} {class_record.teacher.user.last_name}"
            else:
                subject_info['teacher_name'] = "Unknown Teacher"

            student_data['subjects'].append(subject_info)

        # Append student data to the final grades
        final_grades.append(student_data)

    # Compute the general average for each student
    for student_data in final_grades:
        total_final_grade = sum([subject_info['final_grade'] for subject_info in student_data['subjects']])
        num_subjects = len(student_data['subjects'])
        student_data['general_average'] = total_final_grade / num_subjects if num_subjects > 0 else 0
        print(student_data['general_average'])
        print(student_data)
        print(grade)
        print(section)
        save_general_average(student_data, grade, section)
        
    context = {
        'grade': grade,
        'section': section,
        'final_grades': final_grades,
    }

    return render(request, "teacher_template/adviserTeacher/all_final_grades.html", context)

def update_score(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        student_name = request.POST.get('student_name')
        new_score = request.POST.get('new_score')
        column_index = int(request.POST.get('column_index'))
        section_id = request.POST.get('section_id')  # Added section_id for differentiation
        class_record_id = request.POST.get('class_record_id')
        scores_hps = request.POST.get('scores_hps')
        # percentage_score_written_works = request.POST.get('percentage_score_written_works')
        # percentage_score_performance_task = request.POST.get('percentage_score_performance_task')
        # percentage_score_quarterly_assessment = request.POST.get('percentage_score_quarterly_assessment')
        # weighted_score_written_works = request.POST.get('weighted_score_written_works')
        # weighted_score_performance_task = request.POST.get('weighted_score_performance_task')
        # weighted_score_quarterly_assessment = request.POST.get('weighted_score_quarterly_assessment')


        # print("Request POST Data:", request.POST)
        # print("Class Record ID:", class_record_id)
        # print(column_index)
        # print(section_id)  # Add this line for debugging

        student = Student.objects.get(name=student_name)

        try:
            # Retrieve the GradeScores object based on student name and class record id
            grade_score = GradeScores.objects.get(
                   student=student,
                class_record__id=class_record_id
            )

            print("Grade Score Found:", grade_score)  # Add this line for debugging

        except GradeScores.DoesNotExist:
            print(f"Not Found: /update_score/")
            return HttpResponse("GradeScores not found for the given student and class record ID.", status=404)

        #     # Determine the field to update based on the section_id
        # if section_id == 'written_works':
        #     percentage_score = percentage_score_written_works
        #     weighted_score = weighted_score_written_works
        # elif section_id == 'performance_task':
        #     percentage_score = percentage_score_performance_task
        #     weighted_score = weighted_score_performance_task
        # elif section_id == 'quarterly_assessment':
        #     percentage_score = percentage_score_quarterly_assessment
        #     weighted_score = percentage_score_quarterly_assessment
        # else:
        #     return JsonResponse({'error': 'Invalid section_id'})



        if section_id == 'written_works':
            scores_field = 'written_works_scores'
            hps_field = 'scores_hps_written'  # Adjust with your actual field name for HPS
            total_field = 'total_score_written'
            percentage_field = 'percentage_score_written'
            weighted_field = 'weighted_score_written'
            max_field = 'total_ww_hps'  # Adjust with your actual field name for max score
            weight_field = 'weight_input_written'  # Adjust with your actual field name for weight
        elif section_id == 'performance_task':
            scores_field = 'performance_task_scores'
            hps_field = 'scores_hps_performance'  # Adjust with your actual field name for HPS
            total_field = 'total_score_performance'
            percentage_field = 'percentage_score_performance'
            weighted_field = 'weighted_score_performance'
            max_field = 'total_pt_hps'  # Adjust with your actual field name for max score
            weight_field = 'weight_input_performance'  # Adjust with your actual field name for weight
        elif section_id == 'quarterly_assessment':
            scores_field = 'quarterly_assessment_scores'
            hps_field = 'scores_hps_quarterly'  # Adjust with your actual field name for HPS
            total_field = 'total_score_quarterly'
            percentage_field = 'percentage_score_quarterly'
            weighted_field = 'weighted_score_quarterly'
            max_field = 'total_qa_hps'  # Adjust with your actual field name for max score
            weight_field = 'weight_input_quarterly'  # Adjust with your actual field name for weight
        else:
            return JsonResponse({'error': 'Invalid section_id'})

        # Use a dynamic naming convention for total_field
        #  # Ensure scores_list has enough elements, initialize with zeros if necessary
        # scores_list = getattr(grade_score, scores_field, [0] * 10)

       # Ensure scores_list has enough elements, initialize with zeros if necessary
        scores_list = getattr(grade_score, scores_field, [0] * (column_index + 1))

        # Update the specific value in the scores list
        if section_id == 'written_works':
            hps_scores_list = getattr(grade_score, hps_field, [0] * (column_index + 1))
            hps_written = hps_scores_list[column_index]

            if new_score and new_score.strip():
                try:
                    new_score_numeric = int(float(new_score))
                except ValueError:
                    # Set the score to an empty string if it's not a valid numeric value
                    setattr(grade_score, scores_field, [0] * (column_index + 1))
                    return JsonResponse({'success': False, 'error': 'Invalid score. Please enter a numeric value for the written score.'})

                # Check if hps_written is a valid numeric value
                try:
                    hps_written_numeric = int(float(hps_written))
                except ValueError:
                    # Handle the case where hps_written is not a valid numeric value
                    return JsonResponse({'success': False, 'error': 'Invalid Highest Possible score. Please provide a valid numeric value.'})

                if new_score_numeric > hps_written_numeric:
                    # Set the score to an empty string if the condition is met
                    setattr(grade_score, scores_field, [0] * (column_index + 1))
                    return JsonResponse({'success': False, 'error': 'Invalid score. Written score cannot exceed HPS score.'})
        # Add similar logic for performance_task

        elif section_id == 'performance_task':
            hps_scores_list = getattr(grade_score, 'scores_hps_performance', [0] * (column_index + 1))
            hps_performance = hps_scores_list[column_index]

            if new_score and new_score.strip():
                try:
                    new_score_numeric = int(float(new_score))
                except ValueError:
                    # Set the score to an empty string if it's not a valid numeric value
                    setattr(grade_score, scores_field, [0] * (column_index + 1))
                    return JsonResponse({'success': False, 'error': 'Invalid score. Please enter a numeric value for the performance task score.'})

                # Check if hps_performance is a valid numeric value
                try:
                    hps_performance_numeric = int(float(hps_performance))
                except ValueError:
                    # Handle the case where hps_performance is not a valid numeric value
                    return JsonResponse({'success': False, 'error': 'Invalid Highest Possible score score. Please provide a valid numeric value.'})

                if new_score_numeric > hps_performance_numeric:
                    # Set the score to an empty string if the condition is met
                    setattr(grade_score, scores_field, [0] * (column_index + 1))
                    return JsonResponse({'success': False, 'error': 'Invalid score. Performance task score cannot exceed HPS score.'})

                # Add similar logic for quarterly_assessment
        elif section_id == 'quarterly_assessment':
            hps_quarterly = getattr(grade_score, max_field)

            if new_score and new_score.strip():
                try:
                    total_quarterly_numeric = int(float(new_score))
                except ValueError:
                    # Set the score to an empty string if it's not a valid numeric value
                    setattr(grade_score, total_field, 0)
                    return JsonResponse({'success': False, 'error': 'Invalid total score. Please enter a numeric value for the quarterly assessment score.'})

                if total_quarterly_numeric > hps_quarterly:
                    print('Debug: new_score:', new_score)
                    print('Debug: total_quarterly_numeric:', total_quarterly_numeric)
                    print('Debug: hps_quarterly:', hps_quarterly)
                    # Set the score to an empty string if the condition is met
                    setattr(grade_score, total_field, 0)
                    return JsonResponse({'success': False, 'error': 'Invalid total score. Quarterly assessment score cannot exceed HPS score.'})
                              
                              
                                # Update the specific value in the scores list
        if new_score != '' and new_score.strip():  # Check if new_score is not an empty string or contains only whitespace
            scores_list[column_index] = int(float(new_score))
        else:
            scores_list[column_index] = ''  # Or any default value you prefer
# Or any default value you prefer

        # Save the updated scores list to the model
        setattr(grade_score, scores_field, scores_list)


        scores_list = [int(score) if score and score != '' else 0 for score in scores_list]

        if section_id == 'quarterly_assessment':
            # For quarterly assessment, total_score is directly updated
            total_score = int(float(new_score))
            max_value = getattr(grade_score, max_field)
            percentage_score = (total_score / max_value) * 100 if max_value is not None and max_value != 0 else 0
            weighted_score = (percentage_score / 100) * getattr(grade_score, weight_field)
        else:
    # For other sections, calculate total_score from scores_list
            total_score = sum(scores_list)
            max_field_value = getattr(grade_score, max_field)

            # Check if max_field_value is None before performing division
            if max_field_value is not None and max_field_value != 0:
                percentage_score = (total_score / max_field_value) * 100
                weighted_score = (percentage_score / 100) * getattr(grade_score, weight_field)
            else:
                # Handle the case where max_field_value is None (set a default value or handle it as needed)
                percentage_score = 0
                weighted_score = 0
            

        # Log the calculated values
        print("Total Score:", total_score)
        print("Percentage Score:", percentage_score)
        print("Weighted Score:", weighted_score)
        print(scores_hps)

        # Set the calculated values to the model fields
        setattr(grade_score, total_field, int(float(total_score)))
        setattr(grade_score, percentage_field, round(percentage_score, 2))
        setattr(grade_score, weighted_field, round(weighted_score,2))

        
        print(scores_list)
        print(total_field)
        grade_score.save()
        # Return updated data as JSON response
        initial_grade = (
            (getattr(grade_score, 'weighted_score_written', 0) or 0) +
            (getattr(grade_score, 'weighted_score_performance', 0) or 0) +
            (getattr(grade_score, 'weighted_score_quarterly', 0) or 0)
        )
        initial_grade = round(initial_grade, 2)

        transmuted_grades = transmuted_grade(initial_grade)

        # Log the initial grade
        print("Initial Grade:", initial_grade)
        print("transmuted_grade:", transmuted_grades)

        if section_id == 'quarterly_assessment':
            scores_hps_value = None  # or any other default value for quarterly assessment
        else:
            scores_hps_value = getattr(grade_score, hps_field)

        # Set the calculated initial grade to the model field
        setattr(grade_score, 'initial_grades', initial_grade)
        setattr(grade_score, 'transmuted_grades', transmuted_grades)
        grade_score.save()

        # Return updated data as JSON response
        response_data = {
            'success': True,
            'total_score': getattr(grade_score, total_field),
            'percentage_score': getattr(grade_score, percentage_field),
            'weighted_score': getattr(grade_score, weighted_field),
            'initial_grade': initial_grade,  # Add initial grade to the response
            'scores_hps': scores_hps_value,
        }
        
        
        return JsonResponse(response_data)


    return JsonResponse({'error': 'Invalid request'})


def update_highest_possible_scores(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        class_record_id = request.POST.get('class_record_id')
        section_id = request.POST.get('section_id')
        new_hps_data = request.POST.getlist('new_hps_data[]')

        print("Request POST Data:", request.POST)
        print("Class Record ID:", class_record_id)
        print(section_id)

        try:
            # Retrieve GradeScores objects based on the given class record id
            grade_scores = GradeScores.objects.filter(class_record_id=class_record_id)
        except GradeScores.DoesNotExist:
            return JsonResponse({'error': 'GradeScores not found for the given class record ID.'}, status=404)

        # Determine the field to update based on the section_id
        if section_id == 'written_works':
            hps_field = 'scores_hps_written'
            total_hps_field = 'total_ww_hps'
        elif section_id == 'performance_task':
            hps_field = 'scores_hps_performance'
            total_hps_field = 'total_pt_hps'
        elif section_id == 'quarterly_assessment':
            hps_field = 'scores_hps_quarterly'
        else:
            return JsonResponse({'error': 'Invalid section_id'})

        # Update the highest possible scores data for each GradeScores object
        for grade_score in grade_scores:
            # Convert the new_hps_data to a list of integers, handling empty strings
            new_hps_list = [int(float(value)) if value.strip() != '' else '' for value in new_hps_data]

            # Update the scores_hps field with the new list
            setattr(grade_score, hps_field, new_hps_list)
            grade_score.save()

            # Update the total_hps_field
            total_hps_value = sum([int(value) for value in new_hps_list if isinstance(value, int) or (isinstance(value, str) and value.isdigit())])
            setattr(grade_score, total_hps_field, total_hps_value)
            grade_score.save()

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'})

def update_total_max_quarterly(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        class_record_id = request.POST.get('class_record_id')
        new_score = request.POST.get('new_score')

        print("Request POST Data:", request.POST)
        print("Class Record ID:", class_record_id)
        print(new_score)

        try:
            # Retrieve GradeScores objects based on the given class record id
            grade_scores = GradeScores.objects.filter(class_record_id=class_record_id)
        except GradeScores.DoesNotExist:
            return JsonResponse({'error': 'GradeScores not found for the given class record ID.'}, status=404)

        # Determine the field to update based on the section_id
        section_id = 'quarterly_assessment'
        hps_field = 'scores_hps_quarterly'
        total_hps_field = 'total_qa_hps'

        # Update the total_qa_hps for each GradeScores object
        for grade_score in grade_scores:
            try:
                # Convert new_score to an integer (handle empty strings as well)
                total_qa_hps_value = int(float(new_score)) if new_score.strip() != '' else 0

                # Update the total_qa_hps field
                setattr(grade_score, total_hps_field, total_qa_hps_value)
                grade_score.save()

            except Exception as e:
                # Print or log the exception for debugging purposes
                print(f"Error updating grade_score {grade_score.id}: {e}")

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'})


def validate_score(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        student_name = request.POST.get('student_name')
        new_score = request.POST.get('new_score')
        column_index = int(request.POST.get('column_index'))
        section_id = request.POST.get('section_id')
        class_record_id = request.POST.get('class_record_id')

        try:
            grade_score = GradeScores.objects.get(
                student_name=student_name,
                class_record__id=class_record_id
            )
        except GradeScores.DoesNotExist:
            return JsonResponse({'error': 'GradeScores not found for the given student and class record ID.'}, status=404)

        if section_id == 'written_works':
            scores_field = 'written_works_scores'
            hps_field = 'scores_hps_written'
        elif section_id == 'performance_task':
            scores_field = 'performance_task_scores'
            hps_field = 'scores_hps_performance'
        elif section_id == 'quarterly_assessment':
            scores_field = 'quarterly_assessment_scores'
            hps_field = 'scores_hps_quarterly'
        else:
            return JsonResponse({'error': 'Invalid section_id'})

        # Ensure scores_list and hps_list have enough elements, initialize with zeros if necessary
        scores_list = getattr(grade_score, scores_field, [0] * (column_index + 1))
        hps_list = getattr(grade_score, hps_field, [0] * (column_index + 1))

        # Validate the new score against its corresponding HPS
        highest_possible_score_str = hps_list[column_index]
        if highest_possible_score_str != '':
            highest_possible_score = int(highest_possible_score_str)  # Convert HPS to integer
            if new_score != '' and int(new_score) > highest_possible_score:  # Convert score to integer
                return JsonResponse({'error': f'Score cannot be greater than the highest possible score for index {column_index}.'})
        else:
            return JsonResponse({'error': f'Highest possible score is empty for index {column_index}.'})

        # Validate HPS against written scores
        for i, score in enumerate(scores_list):
            if hps_list[i] != '' and int(score) > int(hps_list[i]):
                return JsonResponse({'error': f'Written score cannot be greater than the highest possible score for index {i}.'})

        return JsonResponse({'success': 'Validation passed.'})

    return JsonResponse({'error': 'Invalid request'})


def delete_classrecord(request, class_record_id):
    class_record = get_object_or_404(ClassRecord, id=class_record_id)

    if request.method == 'POST':
        class_record.delete()
        return redirect('class_records_list')  # Redirect to your class records list view

    return render(request, 'teacher_template/adviserTeacher/view_classrecord.html', {'class_record': class_record})

def class_records_list(request):
    class_records = ClassRecord.objects.all()
    return render(request, 'teacher_template/adviserTeacher/view_classrecord.html', {'class_records': class_records})



