
import json
import os
import io
import re

from requests import request

from CuyabSRMS.utils import transmuted_grade, log_activity
from .utils import log_activity
from django import forms
import openpyxl
from django.contrib import messages
from .models import AdvisoryClass, Grade, GradeScores, Section, Student, Teacher, Subject, Quarters, ClassRecord, FinalGrade, GeneralAverage, QuarterlyGrades
from django.contrib.auth import get_user_model  # Add this import statement
from django.urls import reverse
from django.http import HttpResponse

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
from .models import ProcessedDocument, ExtractedData, Section
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
import openpyxl

#Grade
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .forms import GradeScoresForm
from django.views.decorators.http import require_POST
from django.utils import translation
from django.db import transaction
from statistics import mean
from django.core.exceptions import MultipleObjectsReturned
from openpyxl import load_workbook
from django.utils.timezone import now
from django.core.exceptions import MultipleObjectsReturned
import logging

@login_required
def home_teacher(request):
    announcements = Announcement.objects.all()
    return render(request, 'teacher_template/home_teacher.html', {'announcements': announcements})
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

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    try:
        service = build('sheets', 'v4', credentials=creds)

        def get_sheet_values(spreadsheet_id, start_range, end_range):
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{start_range}:{end_range}",
            ).execute()
            values = result.get('values', [])
            return values

        def get_rows(sheet_values):
            rows_list = []

            for i in range(5):
                if i < len(sheet_values):
                    row = sheet_values[i]
                    non_empty_values = [value.strip() for value in row if value.strip() != '']
                    rows_list.append(non_empty_values)
                else:
                    rows_list.append([])

            return rows_list

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

        # Get the values from the existing sheet
        existing_sheet_values = get_sheet_values(spreadsheet_id, "A1", "ZZ1000")

        if existing_sheet_values:
            rows_list = get_rows(existing_sheet_values)
            lrn_data = find_lrn_and_store_as_dict(existing_sheet_values)

            # Extract key-value pairs from the first few rows of the sheet
            terms_to_find = ["School ID", "School Name", "Division", "District", "School Year", "Grade Level", "Section"]
            key_value_pairs = {}

            for i, row in enumerate(rows_list, start=1):
                # Inside the process_google_sheet function
                for term in terms_to_find:
                    if term in row:
                        index = row.index(term)
                        if index + 1 < len(row):
                            key_value_pairs[term.replace(" ", "_")] = row[index + 1]
                        else:
                            key_value_pairs[term.replace(" ", "_")] = None


            # Print LRN data and key-value pairs
            print("LRN Data:")
            print(lrn_data)
            print("Key-Value Pairs:")
            print(key_value_pairs)

            return {'lrn_data': lrn_data, 'key_value_pairs': key_value_pairs}
        else:
            return None
    except Exception as e:
        print(f"An error occurred in process_google_sheet: {e}")
        return None
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
                if len(str(lrn_value)) == 12 and str(lrn_value).isdigit():
                    current_lrn = lrn_value
                    lrn_data[current_lrn] = []
                else:
                    current_lrn = None

                if current_lrn:
                    non_empty_fields = [field for field in row if field is not None and str(field).strip() != '']
                    lrn_data[current_lrn].append(non_empty_fields)

    return lrn_data

def get_rows(sheet_values):
    rows_list = list(sheet_values)[:5]  # Convert the generator to a list and take the first 5 rows

    for i in range(5 - len(rows_list)):
        rows_list.append([])

    # Remove empty fields from each row and strip white spaces
    non_empty_rows = [[str(cell.value).strip() for cell in row if cell.value is not None] for row in rows_list]

    return non_empty_rows

def process_excel_file(file_path):
    try:
        workbook = openpyxl.load_workbook(file_path)
        existing_sheet_name = workbook.sheetnames[0]  # Use the first sheet
        existing_sheet = workbook[existing_sheet_name]
        existing_sheet_values = get_sheet_values(existing_sheet, (1, 1), (existing_sheet.max_row, existing_sheet.max_column))
        row_list = get_rows(existing_sheet.iter_rows())

        if existing_sheet_values:
            lrn_data = find_lrn_and_store_as_dict(existing_sheet_values)

            # Extract key-value pairs from the first few rows of the sheet
            terms_to_find = ["School ID", "School Name", "Division", "District", "School Year", "Grade Level", "Grade", "Section"]
            key_value_pairs = {}

            for i, row in enumerate(row_list, start=1):
                print(f"Processing Row {i}: {row}")  # Add this line to debug

                for term in terms_to_find:
                    if term in row:
                        index = row.index(term)
                        if index + 1 < len(row):
                            key_value_pairs[term.replace(" ", "_")] = row[index + 1]
                        else:
                            key_value_pairs[term.replace(" ", "_")] = None

            # Print LRN data and key-value pairs
            print("LRN Data:")
            print(lrn_data)
            print("Key-Value Pairs:")
            print(key_value_pairs)

            return {'lrn_data': lrn_data, 'key_value_pairs': key_value_pairs}
        else:
            return None
    except Exception as e:
        print(f"An error occurred in process_excel_file: {e}")
        return None
    
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

                result_data = process_google_sheet(spreadsheet_id, sheet_name)

                if result_data is not None:
                    return render(request, 'teacher_template/adviserTeacher/tempo_newupload.html', result_data)
                else:
                    messages.error(request, "Failed to process the Google Sheet")
            else:
                messages.error(request, "Invalid Google Sheet link")
        elif excel_file:
            # Save the uploaded Excel file temporarily
            temp_file_path = 'temp.xlsx'
            valid_excel_extensions = ['.xls', '.xlsx']
            file_extension = os.path.splitext(excel_file.name)[1].lower()

            if file_extension not in valid_excel_extensions:
                messages.error(request, "Invalid Excel file. Please upload a valid Excel file.")
                return render(request, 'teacher_template/adviserTeacher/upload.html')

            # If the file is in .xls format, convert it to .xlsx
            if file_extension == '.xls':
                df = pd.read_excel(excel_file)
                df.to_excel(temp_file_path, index=False)
            else:
                with open(temp_file_path, 'wb') as temp_file:
                    for chunk in excel_file.chunks():
                        temp_file.write(chunk)

            # Process Excel file
            result_data = process_excel_file(temp_file_path)

            if result_data is not None:
                print("LRN Data:")
                print(result_data['lrn_data'])
                print("Key-Value Pairs:")
                print(result_data['key_value_pairs'])
                return render(request, 'teacher_template/adviserTeacher/tempo_newupload.html', result_data)
            else:
                messages.error(request, "Failed to process the Excel File")

        else:
            messages.error(request, "Invalid file")

    return render(request, 'teacher_template/adviserTeacher/tempo_newupload.html')


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

            # Get the data from the request
            school_id = received_data.get('school_id', '')
            district = received_data.get('district', '')
            division = received_data.get('division', '')
            school_name = received_data.get('school_name', '')
            school_year = received_data.get('school_year', '')
            grade_name = received_data.get('grade', '')
            section_name = received_data.get('section', '')
            class_type = received_data.get('classType', '')  # New field for class type

            user = request.user
            action = f'{user} create a Class {grade_name} {section_name}'
            details = f'{user} created a Class named {grade_name} {section_name} in the system.'
            log_activity(user, action, details)

            logs = user, action, details    
            print(logs)

            for item in received_data['rows']:
                lrn = item.get('LRN')
                name = item.get('Name')
                sex = item.get('Sex')
                birthday = item.get('Birthday')

                # Create or update the Grade object
                grade, _ = Grade.objects.get_or_create(name=grade_name)

                # Create or update the Section object
                section, _ = Section.objects.get_or_create(name=section_name, grade=grade, teacher=teacher)

                # Increment the total_students field for the respective section
                section.total_students += 1
                section.class_type = class_type  # Save the class type on Section
                section.save()

                # Initialize or get the existing grade_section dictionary
                teacher.grade_section = teacher.grade_section or {}

                # Save the grade_section in the Teacher model
                teacher.grade_section[grade.name] = section.name
                teacher.save()

                # Create or update the Student object based on LRN and teacher
                student, created = Student.objects.get_or_create(
                    lrn=lrn,
                    teacher=teacher,
                    defaults={
                        'name': name,
                        'sex': sex,
                        'birthday': birthday,
                        'school_id': school_id,
                        'district': district,
                        'division': division,
                        'school_name': school_name,
                        'school_year': school_year,
                        'grade': grade.name,
                        'section': section.name,
                        'class_type': class_type  # Save the class type on Student
                    }
                )

                # Update other fields if needed
                student.name = name
                student.sex = sex
                student.birthday = birthday
                student.school_id = school_id
                student.division = division
                student.district = district
                student.school_name = school_name
                student.school_year = school_year
                student.grade = grade.name
                student.section = section.name
                student.class_type = class_type  # Update the class type on Student

                # Save the associated objects before saving the student
                grade.save()
                section.save()
                student.save()

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
    selected_grade = request.GET.get('grade')
    selected_section = request.GET.get('section')
    print(selected_grade)
    print(selected_section)

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
        'quarters': quarters,
        'selected_grade': selected_grade, 
        'selected_section': selected_section,
    }
    # print("Distinct grades:", grades)
    # print("Distinct sections:", sections)
    # print("Distinct subjects:", subjects)

    return render(request, 'teacher_template/adviserTeacher/new_classrecord.html', context)
   # Replace with the actual URL of your new_classrecord.html
   
def get_sections_classrecord(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        grade_id = request.GET.get('grade_id')
        sections = Student.objects.filter(grade=grade_id).values_list('section', flat=True).distinct()
        sections_list = list(sections)
        return JsonResponse({'sections': sections_list})
    else:
        return JsonResponse({'error': 'Invalid request'})

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
            classrecord_name = f'{grade_name} {section_name} {subject_name} {quarter_name}'

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
            students = Student.objects.filter(grade=grade_name, section=section_name, class_type='Subject')

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
        class_record_name = class_record.name

        user = request.user
        action = f'{user} create a Classrecord "{class_record_name}"'
        details = f'{user} created a Classrecord named "{class_record_name}" in the system.'
        log_activity(user, action, details)

        logs = user, action, details    
        print(logs)

        students = Student.objects.filter(grade=grade_name, section=section_name, class_type='Subject')
        
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
        unique_combinations = students.values('grade', 'section', 'class_type').distinct()

        context = {
            'teacher': teacher,
            'unique_grades_sections': unique_combinations,
        }
        return render(request, 'teacher_template/adviserTeacher/classes.html', context)

    return render(request, 'teacher_template/adviserTeacher/classes.html')

def toggle_class_type_function(student):
    # Toggle the class type for the given student
    if student.class_type == 'Advisory':
        student.class_type = 'Subject'
    else:
        student.class_type = 'Advisory'
    
    # Save the changes
    student.save()

    # Return the updated class type
    return student.class_type


def toggle_class_type(request):
    if request.method == 'POST':
        try:
            # Retrieve the POST data
            data = json.loads(request.body)

            # Extract the grade, section, and current_class_type from the data
            grade = data.get('grade')
            section = data.get('section')
            current_class_type = data.get('current_class_type')

            # Retrieve all students with the given grade and section
            students = Student.objects.filter(grade=grade, section=section)

            # Toggle the class type for each student
            for student in students:
                if current_class_type == 'Advisory':
                    student.class_type = 'Subject'
                else:
                    student.class_type = 'Advisory'

                # Save the changes
                student.save()

            response_data = {'message': 'Class type updated successfully'}
            return JsonResponse(response_data)

        except Exception as e:
            response_data = {'message': f'Error: {str(e)}'}
            return JsonResponse(response_data, status=400)

    response_data = {'message': 'Invalid request method'}
    return JsonResponse(response_data, status=405)

def sf9(request):
    # Query all students from the database
    all_students = Student.objects.all()

    # Pass the queryset to the template context
    context = {'all_students': all_students}

    # Render the template with the context
    return render(request, 'teacher_template/adviserTeacher/sf9.html', context)

@login_required
def delete_student(request, grade, section):
    user = request.user
            


    if user.user_type == 2:
        teacher = get_object_or_404(Teacher, user=user)
        students = Student.objects.filter(grade=grade, section=section, teacher=teacher)

        if students.exists():
            # Assuming you have some permission checks here before deleting
            students.delete()

            # Delete associated ClassRecord records
            ClassRecord.objects.filter(grade=grade, section=section, teacher=teacher).delete()

            action = f'{user} delete a Class name {grade} {section}'
            details = f'{user} deleted a Class named {grade} {section} in the system.'
            log_activity(user, action, details)

                # Redirect to a different page after deletion
            return redirect('display_students')  # Replace with your actual view name
        else:
            # Redirect to a different page if no students found
            return redirect('display_students')  # Replace with your actual view name

    # If the user is not a teacher or if the permissions check fails
    return JsonResponse({'message': 'Unable to delete students. Permission denied.'}, status=403)

def student_list_for_subject(request):
    # Assuming the user is logged in
    user = request.user

    # Check if the user is a teacher
    if user.is_authenticated and hasattr(user, 'teacher'):
        # Retrieve the teacher associated with the user
        teacher = user.teacher

        grade = request.GET.get('grade')
        section = request.GET.get('section')
        class_type = request.GET.get('class_type')
        
        # Filter class records based on the teacher
        class_records = ClassRecord.objects.filter(teacher=teacher, grade=grade, section=section)

        # Fetch students based on grade and section
        students = Student.objects.filter(grade=grade, section=section, class_type=class_type)

        # Fetch distinct subjects based on grade and section
        subjects = ClassRecord.objects.filter(grade=grade, section=section).values('subject').distinct()

        top_students = (
            GeneralAverage.objects.filter(grade=grade, section=section)
            .order_by('-general_average')[:10]
            
        )

    context = {
        'grade': grade,
        'section': section,
        'class_type': class_type,
        'students': students,
        'class_records': class_records,
        'subjects': subjects,
        'top_students': top_students,
        
    }

    return render(request, 'teacher_template/adviserTeacher/student_list_for_subject.html', context)

def student_list_for_advisory(request):
    # Assuming the user is logged in
    user = request.user

    # Check if the user is a teacher
    if user.is_authenticated and hasattr(user, 'teacher'):
        # Retrieve the teacher associated with the user
        teacher = user.teacher

        grade = request.GET.get('grade')    
        section = request.GET.get('section')
        class_type = request.GET.get('class_type')
        
        
        # Fetch students based on grade and section
        students = Student.objects.filter(grade=grade, section=section, class_type=class_type)
        # Fetch advisory classes based on teacher, grade, and section
        advisory_classes = AdvisoryClass.objects.filter(grade=grade, section=section).values('subject', 'from_teacher_id').distinct()
        quarters = advisory_classes.values_list('first_quarter', 'second_quarter', 'third_quarter', 'fourth_quarter').distinct()
       
        context = {
            'grade': grade,
            'section': section,
            'advisory_classes': advisory_classes,
            'students': students,
            'quarters': quarters,
            'class_type': class_type,
           
        }
    return render(request, 'teacher_template/adviserTeacher/student_list_for_advisory.html', context)

def display_advisory_data(request):
        # Assuming the user is logged in
    user = request.user

    # Check if the user is a teacher
    if user.is_authenticated and hasattr(user, 'teacher'):
        # Retrieve the teacher associated with the user
        teacher = user.teacher

        grade = request.GET.get('grade')    
        section = request.GET.get('section')
        class_type = request.GET.get('class_type')
        subject = request.GET.get('subject')
        
        
        # Fetch students based on grade and section
        students = Student.objects.filter(grade=grade, section=section, class_type=class_type)
        # Fetch advisory classes based on teacher, grade, and section
        advisory_classes = AdvisoryClass.objects.filter(grade=grade, section=section, subject=subject)

       
        context = {
            'grade': grade,
            'subject': subject,
            'section': section,
            'advisory_classes': advisory_classes,
            'students': students,
            'class_type': class_type,
           
        }
            
    return render(request, 'teacher_template/adviserTeacher/subject_quarter_advisory.html', context)


def display_student_transmuted_grades(request):
    grade = request.GET.get('grade')
    section = request.GET.get('section')
    subject = request.GET.get('subject')
    teacher_id = request.GET.get('teacher_id')

    advisory_classes = AdvisoryClass.objects.filter(grade=grade, section=section, subject=subject, from_teacher_id=teacher_id)

    context = {
        'advisory_classes': advisory_classes,
    }

    return render(request, 'teacher_template/adviserTeacher/advisory_final_grade_subject.html', context)


    
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

    # Handle None values for initial_grades and transmuted_grades
    for grade_score in grade_scores:
        if grade_score.initial_grades is None:
            grade_score.initial_grades = ""
        if grade_score.transmuted_grades is None:
            grade_score.transmuted_grades = ""

    context = {
        'class_record': class_record,
        'grade_scores': grade_scores,
    }

    return render(request, "teacher_template/adviserTeacher/summary_of_quarterly_grade.html", context)




def grade_summary(request, grade, section, quarter):
    students = FinalGrade.objects.filter(grade=grade, section=section)

    # Dictionary to store subject-wise grades and average score for each student
    subject_grades = {}
    quarter_mapping = {
        '1st Quarter': '1st Quarter',
        '2nd Quarter': '2nd Quarter',
        '3rd Quarter': '3rd Quarter',
        '4th Quarter': '4th Quarter',
    }

    # Fetch subject-wise grades for each student
    for student in students:
        subjects = get_subjects(student.student)
        subject_grades[student.student.name] = {}
        grades = []  # List to store grades for calculating mean
        for subject in subjects:
            db_quarter = quarter_mapping.get(quarter, quarter)
            subject_grade = get_subject_score(student.student, subject, db_quarter)
            print(subject_grade)
            subject_grades[student.student.name][subject] = subject_grade
            if subject_grade is not None:
                grades.append(subject_grade)

        # Calculate average score
        if grades:
            subject_grades[student.student.name]['average_score'] = round(mean(grades), 2)
        else:
            subject_grades[student.student.name]['average_score'] = None

        # Check if QuarterlyGrades entry already exists for this student and quarter
        existing_entry = QuarterlyGrades.objects.filter(student=student.student, quarter=quarter).first()
        if not existing_entry:
            # Save grades to QuarterlyGrades model
            QuarterlyGrades.objects.create(
                student=student.student,
                quarter=quarter,
                grades=subject_grades[student.student.name]
            )
        elif existing_entry.grades != subject_grades[student.student.name]:
            # Update the existing entry if the grades are different
            existing_entry.grades = subject_grades[student.student.name]
            existing_entry.save()

    subjects = get_subjects(students.first().student) if students else []

    context = {
        'students': students,
        'subject_grades': subject_grades,
        'subjects': subjects,
        'quarter': quarter,
    }

    return render(request, 'teacher_template/adviserTeacher/quarterly_summary.html', context)


def get_subject_score(student, subject, quarter):
    try:
        # Fetch the FinalGrade instance for the given student, subject, and quarter
        grade_instance = FinalGrade.objects.get(
            student=student,
            grade=student.grade,
            section=student.section,
        )
        
        # Access the final_grade JSONField and retrieve the score for the given subject and quarter
        final_grade_data = json.loads(grade_instance.final_grade)  # Assuming final_grade is a JSON string
        
        # Loop through each entry in final_grade_data
        for entry in final_grade_data:
            if entry.get('subject') == subject:
                # Check if the quarter grades exist for the subject
                quarter_grades = entry.get('quarter_grades', {})
                subject_score = quarter_grades.get(quarter)
                return subject_score  # Return the score if found
        
        # If subject or quarter not found, return None
        return None

    except FinalGrade.DoesNotExist:
        # Handle the case where the FinalGrade record does not exist
        return None

    except MultipleObjectsReturned:
        # Handle the case where multiple FinalGrade records are returned
        # For example, you can log a warning or return a default value
        return None

    except json.JSONDecodeError:
        # Handle JSON decoding error
        # Log the error or return None
        return None
    
def get_subjects(student):
    # Fetch unique subjects for the given student from the GradeScores model
    subjects = GradeScores.objects.filter(
        student=student,  # Update this line to use the actual Student object
    ).values_list('class_record__subject', flat=True).distinct()

    return [subject for subject in subjects if subject]




def calculate_save_final_grades(grade, section, subject, students, subjects):
    quarters = ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter']

    for student in students:
        student_final_grades = {}  # Store final grades for all subjects for this student
            
        # Check if a record already exists in the FinalGrade model
        existing_final_grade = FinalGrade.objects.filter(
            teacher__classrecord__grade=grade,
            teacher__classrecord__section=section,
            student=student
        ).first()

        if existing_final_grade:
            final_grade_info = json.loads(existing_final_grade.final_grade)  # Convert JSON string to dictionary
            student_final_grades = {item.get('subject'): item for item in final_grade_info}

        for subject_data in subjects:
            subject_name = subject_data.subject

            # Initialize subject data
            subject_info = {'subject': subject_name, 'quarter_grades': {}, 'final_grade': 0}

            # Retrieve initial grades per quarter
            for quarter in quarters:
                grade_score = GradeScores.objects.filter(
                    class_record__grade=grade,
                    class_record__section=section,
                    class_record__subject=subject_name,
                    class_record__quarters=quarter,
                    student=student
                ).first()

                subject_info['quarter_grades'][quarter] = grade_score.transmuted_grades if grade_score else 0

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

            # Store subject info in the dictionary under the subject name
            student_final_grades[subject_name] = subject_info

        final_grade_data = {
            'teacher': class_record.teacher,
            'student': student,
            'grade': grade,
            'subject': subject,
            'section': section,
            'final_grade': json.dumps(list(student_final_grades.values()))  # Convert dictionary values to list and then to JSON string
        }

        if existing_final_grade:
            # Update existing record
            existing_final_grade.final_grade = json.dumps(list(student_final_grades.values()))
            existing_final_grade.save()
        else:
            # Insert new record
            final_grade = FinalGrade.objects.create(**final_grade_data)


def display_final_grades(request, grade, section, subject):
    try:
        teacher = request.user.teacher
        students = Student.objects.filter(grade=grade, section=section)
        
        # Filter subjects to only include the specified subject
        subjects = ClassRecord.objects.filter(grade=grade, section=section, subject=subject, teacher_id=teacher)

        calculate_save_final_grades(grade, section, subject, students, subjects)

        final_grades = []
        for student in students:
            student_data = {'id': student.id, 'name': student.name, 'grade': grade, 'section': section, 'subjects': []}

            # Retrieve final grades from the FinalGrade model
            final_grade = FinalGrade.objects.filter(
                teacher__classrecord__grade=grade,
                teacher__classrecord__section=section,
                student=student
            ).first()

            if final_grade:
                final_grade_info = json.loads(final_grade.final_grade)  # Convert JSON string to list of dictionaries
                for subject_info in final_grade_info:
                    if subject_info['subject'] == subject:  # Filter by subject
                        subject_data = {
                            'subject': subject_info.get('subject', 'Unknown Subject'),
                            'quarter_grades': subject_info['quarter_grades'],
                            'final_grade': subject_info['final_grade'],
                            'teacher_name': subject_info['teacher_name']
                        }
                        student_data['subjects'].append(subject_data)

            # Append student data to the final grades
            final_grades.append(student_data)

        context = {
            'grade': grade,
            'section': section,
            'final_grades': final_grades,
            'subject': subject,  # Pass the subject to the template
        }

        return render(request, "teacher_template/adviserTeacher/final_grades.html", context)
    
    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred: {str(e)}")
        # Return an HTTP 500 Internal Server Error response
        return HttpResponse("Internal Server Error", status=500)




def save_general_average(student_data, grade, section):
    # Check if 'general_average' key is present in student_data and is not None
    if 'general_average' in student_data and student_data['general_average'] is not None:
        # Extract relevant information from student_data
        student = student_data['student']
        general_average = round(student_data['general_average'], 2)

        # Filter GeneralAverage objects based on student, grade, and section
        general_average_records = GeneralAverage.objects.filter(
            student=student,
            grade=grade,
            section=section,
        )

        # Check if any records exist
        if general_average_records.exists():
            # Update the first record
            general_average_record = general_average_records.first()
            general_average_record.general_average = general_average
            general_average_record.save()
        else:
            # Create a new record if none exist
            GeneralAverage.objects.create(
                student=student,
                grade=grade,
                section=section,
                general_average=general_average
            )



def display_all_final_grades(request, grade, section):
    try:
        students = Student.objects.filter(grade=grade, section=section)
        # Fetch all distinct subjects for the specified grade and section
        subjects = ClassRecord.objects.filter(grade=grade, section=section).values('subject').distinct()

        final_grades = []
        for student in students:
            student_data = {'id': student.id, 'name': student.name, 'grade': grade, 'section': section, 'subjects': [], 'student': student}

            for subject in subjects:
                subject_name = subject['subject']
                subject_info = {'name': subject_name, 'quarter_grades': {}, 'final_grade': 0}

                # Retrieve final grades from the FinalGrade model
                final_grade = FinalGrade.objects.filter(
                    teacher__classrecord__grade=grade,
                    teacher__classrecord__section=section,
                    student=student,
                ).first()

                if final_grade:
                    final_grade_data = final_grade.final_grade
                    if isinstance(final_grade_data, str):  # Check if the data is a string
                        final_grade_data = json.loads(final_grade_data)  # Parse JSON string to dictionary

                    # Find the subject entry in final_grade_data
                    for entry in final_grade_data:
                        if entry['subject'] == subject_name:
                            subject_info['final_grade'] = entry['final_grade']
                            subject_info['quarter_grades'] = entry['quarter_grades']
                            break  # Stop searching once the subject is found

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
            save_general_average(student_data, grade, section)
            
        context = {
            'grade': grade,
            'section': section,
            'final_grades': final_grades,
        }

        return render(request, "teacher_template/adviserTeacher/all_final_grades.html", context)
    
    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred while displaying all final grades: {str(e)}")
        # Return an HTTP 500 Internal Server Error response
        return HttpResponse("Internal Server Error", status=500)


    

@transaction.atomic
def update_score(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        student_name = request.POST.get('student_name')
        new_score = request.POST.get('new_score')
        column_index = int(request.POST.get('column_index'))
        section_id = request.POST.get('section_id')  # Added section_id for differentiation
        class_record_id = request.POST.get('class_record_id')
        scores_hps = request.POST.get('scores_hps')


         # Assuming you want to filter students by both name and teacher
        students = Student.objects.filter(name=student_name, teacher=request.user.teacher)

        # Ensure there is exactly one matching student
        if students.count() == 1:
            student = students.first()
        else:
            # Handle the case where there are zero or multiple matching students
            print(f"Error: Found {students.count()} students with the name '{student_name}' for the logged-in teacher.")
            # Add your error handling logic here, e.g., returning an error response.
            return JsonResponse({'success': False, 'error': 'Error in finding the student'})

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

        class_record = grade_score.class_record

        # Save the changes to ClassRecord
        class_record.save()

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
            total_hps_field = 'total_qa_hps'
        else:
            return JsonResponse({'error': 'Invalid section_id'})

        # Update the highest possible scores data for each GradeScores object
        for grade_score in grade_scores:
            # Convert the new_hps_data to a list of integers, handling empty strings
            new_hps_list = [int(value) if value.strip() != '' else '' for value in new_hps_data]

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
            # Assuming you want to filter GradeScores by student name and class record ID
            grade_score = GradeScores.objects.get(
                student__name=student_name,
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



@require_POST
def delete_classrecord(request, class_record_id):
    class_record = get_object_or_404(ClassRecord, id=class_record_id)
    user = request.user
    class_record_name = class_record.name

    # Assuming you have some permission checks here before deleting

    # Delete associated GradeScores records based on class record id
    GradeScores.objects.filter(class_record_id=class_record_id).delete()

    action = f'{user} deleted a Classrecord named "{class_record_name}"'
    details = f'{user} deleted a Classrecord named "{class_record_name}" in the system along with its GradeScores.'
    log_activity(user, action, details)

    # Now, delete the ClassRecord
    class_record.delete()

    return JsonResponse({'message': 'Record deleted successfully'})

# Your other views remain the same
def class_records_list(request):
    class_records = ClassRecord.objects.all()
    return render(request, 'teacher_template/adviserTeacher/view_classrecord.html', {'class_records': class_records})

def tempo_newupload(request):
    return render(request, 'teacher_template/adviserTeacher/tempo_newupload.html')

def read_excel_values(excel_file, sheet_name):
    # Loading the workbook
    wb = load_workbook(filename=excel_file, data_only=True)
    sheet = wb[sheet_name]

    data = []
    start_reading = False

    for row in sheet.iter_rows():
        row_values = []
        for cell in row[1:]:
            cell_value = cell.value
            row_values.append(cell_value)
        
        if any(cell_value is not None and cell_value != 0 for cell_value in row_values):
            if any(isinstance(cell_value, str) and ("MALE" in cell_value or "FEMALE" in cell_value) for cell_value in row_values):
                start_reading = True
            
            if start_reading:
                data.append(row_values)

    return data


def process_row(row):
    # Find the index of the first non-None element after index 0
    index = 1
    while index < len(row) and row[index] is None:
        index += 1

    # Remove the three None values next to index 0
    row = [row[0]] + row[index:]

    # Find the index of the last non-None element
    last_index = len(row) - 1
    while last_index >= 0 and row[last_index] is None:
        last_index -= 1

    # Remove all None values from the end of the list until reaching a non-None value
    row = row[:last_index + 1]

    return row

def divide_scores(score_list):
    written_works_scores = score_list[:10]
    
    # Check if there are enough elements in the score_list for written works
    if len(score_list) >= 13:
        total_scores_written = score_list[10]
        percentage_score_written = score_list[11]
        weighted_score_written = score_list[12]
    else:
        # Set default values if there are not enough elements for written works
        total_scores_written = None
        percentage_score_written = None
        weighted_score_written = None
    
    written_works_dict = {
        "written_works_scores": written_works_scores,
        "total_scores_written": total_scores_written,
        "percentage_score_written": percentage_score_written,
        "weighted_score_written": weighted_score_written
    }

    # Extract Performance Task scores and related values
    performance_task_scores = score_list[13:23]
    
    # Check if there are enough elements in the score_list for performance task
    if len(score_list) >= 26:
        total_score_performance = score_list[23]
        percentage_score_performance = score_list[24]
        weighted_score_performance = score_list[25]
    else:
        # Set default values if there are not enough elements for performance task
        total_score_performance = None
        percentage_score_performance = None
        weighted_score_performance = None
    
    performance_task_dict = {
        "performance_task_scores": performance_task_scores,
        "total_score_performance": total_score_performance,
        "percentage_score_performance": percentage_score_performance,
        "weighted_score_performance": weighted_score_performance
    }

    # Check if there are enough elements in the score_list for Quarterly Assessment
    if len(score_list) >= 29:
        quarterly_assessment = {
            "total_score_quarterly": score_list[26],
            "percentage_score_quarterly": score_list[27],
            "weighted_score_quarterly": score_list[28]
        }
    else:
        quarterly_assessment = None
    
    # Check if there are enough elements in the score_list for Initial Grade
    if len(score_list) >= 30:
        initial_grade = {"initial_grades": score_list[29]}
    else:
        initial_grade = None
    
    # Check if there are enough elements in the score_list for Quarterly Grade
    if len(score_list) >= 31:
        quarterly_grade = {"transmuted_grades": score_list[30]}
    else:
        quarterly_grade = None
    
    return {
        "WRITTEN WORKS": written_works_dict,
        "PERFORMANCE TASK": performance_task_dict,
        "QUARTERLY ASSESSMENT": quarterly_assessment,
        "INITIAL GRADE": initial_grade,
        "QUARTERLY GRADE": quarterly_grade
    }



def class_record_details(excel_file, sheet_name):
    wb = load_workbook(filename=excel_file, data_only=True)
    sheet = wb[sheet_name]

    teacher_row = None
    school_row = None

    for row in sheet.iter_rows():
        row_values = [cell.value for cell in row if cell.value is not None]  # Filter out None values
        
        if "TEACHER:" in row_values:
            grade_section = row_values[2].split('-')
            if len(grade_section) > 1:
                quarter = map_quarter(row_values[0])  # Map the quarter using the map_quarter function
                grade = grade_section[0].strip()
                section = grade_section[1].strip()
                # Map the grade using the map_grade function
                grade = map_grade(grade)
                teacher_row = {
                    "quarters": quarter,
                    "grade": grade,
                    "section": section,
                    "subject": row_values[6]
                }
            else:
                print("Grade section not formatted correctly:", row_values[2])
        
        if "SCHOOL NAME" in row_values:
            school_row = {
                "school_name": row_values[1],
                "school_id": row_values[3],
                "school_year": row_values[5]
            }

        if "REGION" in row_values:
            region_row = {
                "region": row_values[1],
                "division": row_values[3],
                "district": row_values[5]
            }

        if teacher_row and school_row and region_row:
            break

    return teacher_row, school_row, region_row


def divide_hps(row):
    # Divide into sections
    hps_written_works = row[:13]
    hps_performance = row[13:26]
    hps_quarterly = row[26:]

    # Extract values for hps_written_works
    scores_hps_written = hps_written_works[:10]
    total_ww_hps = hps_written_works[10]
    percentage_hps_written = hps_written_works[11]
    weight_input_written = hps_written_works[12]

    # Extract values for hps_performance
    scores_hps_performance = hps_performance[:10]
    total_pt_hps = hps_performance[10]
    percentage_hps_performance = hps_performance[11]
    weight_input_performance = hps_performance[12]

    # Extract values for hps_quarterly
    total_qa_hps = hps_quarterly[0]
    percentage_hps_quarterly = hps_quarterly[1]
    weight_input_quarterly = hps_quarterly[2]

    return {
        "hps_written_works": {
            "scores_hps_written": scores_hps_written,
            "total_ww_hps": total_ww_hps,
            "percentage_hps_written": percentage_hps_written,
            "weight_input_written": weight_input_written
        },
        "hps_performance": {
            "scores_hps_performance": scores_hps_performance,
            "total_pt_hps": total_pt_hps,
            "percentage_hps_performance": percentage_hps_performance,
            "weight_input_performance": weight_input_performance
        },
        "hps_quarterly": {
            "total_qa_hps": total_qa_hps,
            "percentage_hps_quarterly": percentage_hps_quarterly,
            "weight_input_quarterly": weight_input_quarterly
        }
    }


def find_highest_possible_scores(excel_file, sheet_name):
    wb = load_workbook(filename=excel_file, data_only=True)
    sheet = wb[sheet_name]

    hps_row = None

    for row in sheet.iter_rows():
        row_values = [cell.value for cell in row]
        
        # Check if the row contains the header "HIGHEST POSSIBLE SCORE" or "HIGHEST POSSIBLE SCORES"
        if "HIGHEST POSSIBLE SCORE" in row_values:
            # Exclude the first element (index 0) from the row_values list
            row_values = row_values[1:]
            # Process the row to remove leading and trailing None values
            hps_row = process_row(row_values)
            break

    return [hps_row] if hps_row is not None else []

def map_grade(grade):
    grade_map = {
        '1': 'Grade 1',
        'one': 'Grade 1',
        'grade 1': 'Grade 1',
        'GRADE ONE': 'Grade 1',
        '2': 'Grade 2',
        'two': 'Grade 2',
        'grade 2': 'Grade 2',
        'GRADE TWO': 'Grade 2',
        '3': 'Grade 3',
        'three': 'Grade 3',
        'grade 3': 'Grade 3',
        'GRADE THREE': 'Grade 3',
        '4': 'Grade 4',
        'four': 'Grade 4',
        'grade 4': 'Grade 4',
        'GRADE FOUR': 'Grade 4',
        '5': 'Grade 5',
        'five': 'Grade 5',
        'grade 5': 'Grade 5',
        'GRADE FIVE': 'Grade 5',
        '6': 'Grade 6',
        'six': 'Grade 6',
        'grade 6': 'Grade 6',
        'I': 'Grade 1',
        'II': 'Grade 2',
        'III': 'Grade 3',
        'IV': 'Grade 4',
        'V': 'Grade 5',
        'VI': 'Grade 6',

    }
    return grade_map.get(grade.lower(), 'Unknown Grade')

def map_quarter(quarter):
    quarter_map = {
        '1': '1st Quarter',
        'first quarter': '1st Quarter',
        'first': '1st Quarter',
        '1st': '1st Quarter',
        '2': '2nd Quarter',
        'second quarter': '2nd Quarter',
        'second': '2nd Quarter',
        '2nd': '2nd Quarter',
        '3': '3rd Quarter',
        'third quarter': '3rd Quarter',
        'third': '3rd Quarter',
        '3rd': '3rd Quarter',
        '4': '4th Quarter',
        'fourth quarter': '4th Quarter',
        'fourth': '4th Quarter',
        '4th': '4th Quarter',
        '1ST QUARTER': '1st Quarter',
        'FIRST QUARTER': '1st Quarter',
        '2ND QUARTER': '2nd Quarter',
        'SECOND QUARTER': '2nd Quarter',
        '3RD QUARTER': '3rd Quarter',
        'THIRD QUARTER': '3rd Quarter',
        '4TH QUARTER': '4th Quarter',
        'FOURTH QUARTER': '4th Quarter',
    }
    return quarter_map.get(quarter.lower(), 'Unknown Quarter')

def map_data_to_model(json_data, teacher_id, request):
    # Initialize messages list
    messages_list = []
    success = True
    try:
        # Extract details from JSON
        teacher_info = json_data['details']['teacher_info']
        students_scores = json_data['students_scores']
        hps_class_record = json_data['hps_class_record']['HIGHEST POSSIBLE SCORE']

        # Create ClassRecord instance
        class_record_instance = ClassRecord.objects.create(
            name=f"{teacher_info['grade']} - {teacher_info['section']} - {teacher_info['subject']} - {teacher_info['quarters']}",
            grade=teacher_info['grade'],
            section=teacher_info['section'],
            subject=teacher_info['subject'],
            quarters=teacher_info['quarters'],
            teacher_id=teacher_id
        )

        # Iterate over student names in JSON data
        for student_name, student_data in students_scores.items():
            # Find the student with the same name and teacher ID
            try:
                student = Student.objects.get(name=student_name, teacher_id=teacher_id)
            except Student.DoesNotExist:
                messages_list.append(('error', f"Student '{student_name}' does not exist in the database for the provided criteria."))
                continue  # Skip this student if not found

            try:
                # Function to replace None values with empty strings in a list
                def replace_none_with_empty(lst):
                    return ["" if item is None else item for item in lst]

                # Now, when saving GradeScores instance, preprocess the lists
                GradeScores.objects.create(
                    student=student,
                    class_record=class_record_instance,
                    scores_hps_written=replace_none_with_empty(hps_class_record.get('hps_written_works', {}).get('scores_hps_written', [])),
                    scores_hps_performance=replace_none_with_empty(hps_class_record.get('hps_performance', {}).get('scores_hps_performance', [])),
                    total_ww_hps=hps_class_record['hps_written_works'].get('total_ww_hps', ""),
                    total_pt_hps=hps_class_record['hps_performance'].get('total_pt_hps', ""),
                    total_qa_hps=hps_class_record['hps_quarterly'].get('total_qa_hps', ""),
                    written_works_scores=replace_none_with_empty(student_data.get('WRITTEN WORKS', {}).get('written_works_scores', [])),
                    performance_task_scores=replace_none_with_empty(student_data.get('PERFORMANCE TASK', {}).get('performance_task_scores', [])),
                    initial_grades=student_data.get('INITIAL GRADE', {}).get('initial_grades', ""),
                    transmuted_grades=student_data.get('QUARTERLY GRADE', {}).get('transmuted_grades', ""),
                    total_score_written=student_data.get('WRITTEN WORKS', {}).get('total_scores_written', ""),
                    total_score_performance=student_data.get('PERFORMANCE TASK', {}).get('total_score_performance', ""),
                    total_score_quarterly=student_data.get('QUARTERLY ASSESSMENT', {}).get('total_score_quarterly', ""),
                    percentage_score_written=student_data.get('WRITTEN WORKS', {}).get('percentage_score_written', ""),
                    percentage_score_performance=student_data.get('PERFORMANCE TASK', {}).get('percentage_score_performance', ""),
                    percentage_score_quarterly=student_data.get('QUARTERLY ASSESSMENT', {}).get('percentage_score_quarterly', ""),
                    weight_input_written=int(hps_class_record['hps_written_works'].get('weight_input_written', "") * 100),
                    weight_input_performance=int(hps_class_record['hps_performance'].get('weight_input_performance', "") * 100),
                    weight_input_quarterly=int(hps_class_record['hps_quarterly'].get('weight_input_quarterly', "") * 100),
                    weighted_score_written=student_data.get('WRITTEN WORKS', {}).get('weighted_score_written', ""),
                    weighted_score_performance=student_data.get('PERFORMANCE TASK', {}).get('weighted_score_performance', ""),
                    weighted_score_quarterly=student_data.get('QUARTERLY ASSESSMENT', {}).get('weighted_score_quarterly', "")
                )
            except Exception as e:
                messages_list.append(('error', f"Error occurs in student '{student_name}': {e}"))

        # Add success message
        messages_list.append(('success', 'Class record uploaded successfully.'))

    except Exception as e:
        messages_list.append(('error', f"Error code: {e}"))
        success = False

    # Loop through messages list and add messages to request
    for message_type, message_text in messages_list:
        if message_type == 'success':
            messages.success(request, message_text)
        elif message_type == 'error':
            messages.error(request, message_text)

    return success


@login_required
@require_POST
def class_record_upload(request):
    if request.method == 'POST':
        excel_file = request.FILES['excel_file']
        sheet_name = request.POST.get('sheet_name')
        try:
            class_record_data = read_excel_values(excel_file, sheet_name)

            # Process each row in class_record_data
            class_record_data_scores = [process_row(row) for row in class_record_data]

            # Create a dictionary where student's name is the key and the rest of the row values are stored as a list
            class_record_data_scores_with_names = {}
            for row in class_record_data_scores:
                # Check if the student name contains 'FEMALE' or 'MALE'
                if "FEMALE" not in row[0]:
                    student_name = row[0]
                    student_info = {'student_name': student_name}
                    
                    # Find the index of the first non-zero and non-None value
                    index = 1
                    while index < len(row) and (row[index] == 0 or row[index] is None):
                        index += 1

                    # Remove leading occurrences of 0 or None
                    cleaned_row = row[index:] if index < len(row) else []

                    # Update the dictionary with the cleaned row values
                    student_info.update(divide_scores(cleaned_row))
                    class_record_data_scores_with_names[student_name] = student_info


            # Remove the first student from the dictionary
            if class_record_data_scores_with_names:
                del class_record_data_scores_with_names[next(iter(class_record_data_scores_with_names))]

            # Store the result as JSON in the variable students_scores
            students_scores = class_record_data_scores_with_names

            teacher_info, school_info, region_info = class_record_details(excel_file, sheet_name)
            
            highest_possible_scores = find_highest_possible_scores(excel_file, sheet_name)
            highest_possible_scores_with_label = {}

            for row in highest_possible_scores:
                hps_label = row.pop(0)
                highest_possible_scores_with_label[hps_label] = divide_hps(row)

            hps_class_record = highest_possible_scores_with_label

            # Store both results in a single dictionary
            extracted_class_record = {
                "details": {
                    "teacher_info": teacher_info,
                    "school_info": school_info,
                    "region_info": region_info
                },
                "students_scores": students_scores,
                "hps_class_record": hps_class_record
            }
            
            # Save extracted_class_record as a JSON file
            json_filename = 'result.json'
            json_path = os.path.join(settings.MEDIA_ROOT, json_filename)

            # Ensure the directory exists, if not create it
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            with open(json_path, 'w') as json_file:
                json.dump(extracted_class_record, json_file, indent=4)  
            
            # Map the loaded JSON data to the model
            success = map_data_to_model(extracted_class_record, request.user.teacher.id, request)  # Passing request object

            if success:
                return render(request, 'teacher_template/adviserTeacher/class_record_from_excel.html')
            else:
                # If there's an error, return the same template with an error flag
                return render(request, 'teacher_template/adviserTeacher/class_record_from_excel.html', {'error': True})
        except Exception as e:
            # Add error message
            messages.error(request, f'Error processing file: {e}')

        return render(request, 'teacher_template/adviserTeacher/class_record_from_excel.html')
    else:
        # Return a response in case of non-POST requests
        return HttpResponse("Only POST requests are allowed.")
