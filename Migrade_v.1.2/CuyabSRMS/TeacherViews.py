import json
import os

import io
import re

from CuyabSRMS.utils import transmuted_grade
from django import forms
import openpyxl
from django.contrib import messages
from django.shortcuts import render
from .models import Grade, GradeScores, Section, Student, Teacher, Subject, Quarters
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

            # Convert .xls to .xlsx using pandas
            xls_data = pd.read_excel(temp_file_path, sheet_name=None, header=None)
            sheets = list(xls_data.keys())

            if sheets:
                # Use the first sheet in the Excel file
                existing_sheet_name = sheets[0]
            else:
                os.remove(temp_file_path)  # Remove temporary file
                return render(request, 'teacher_template/adviserTeacher/upload.html', {
                    'message': "No sheets found in the Excel file",
                })

            xls_data[existing_sheet_name].to_excel(temp_file_path, index=False, header=None)

            # Load the Excel workbook
            workbook = openpyxl.load_workbook(temp_file_path)

            # Get the values from the existing sheet
            existing_sheet = workbook[existing_sheet_name]
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
    # Retrieve a list of grades and sections that don't have a teacher associated
    grades = Grade.objects.all().values('id', 'name')
    sections = Section.objects.filter(teacher__isnull=True).values('id', 'name')

    # Convert the grades and sections to a dictionary
    data = {
        'grades': list(grades),
        'sections': list(sections),
    }

    return JsonResponse(data)


def class_record(request):
    return render(request, 'teacher_template/adviserTeacher/class_record.html')


def get_grade_details(request):
    grades = Student.objects.values_list('grade', flat=True).distinct()
    sections = Student.objects.values_list('section', flat=True).distinct()
    subjects = Subject.objects.values_list('name', flat=True).distinct()
    quarters = Quarters.objects.values_list('quarters', flat=True).distinct()

    context = {
        'grades': grades,
        'sections': sections,
        'subjects': subjects,
        'quarters': quarters
    }
    # print("Distinct grades:", grades)
    # print("Distinct sections:", sections)
    # print("Distinct subjects:", subjects)

    return render(request, 'teacher_template/adviserTeacher/new_classrecord.html', context)

# views.py
def get_students_by_grade_and_section(request):
    if request.method == "POST":
        grade_name = request.POST.get("grade")
        section_name = request.POST.get("section")
        subject_name = request.POST.get("subject")

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
            scores = GradeScores.objects.filter(student_name=student_name)

            # Store the scores in the dictionary with the student's name as the key
            student_scores[student_name] = scores

        context = {
            'students': students,
            'student_scores': student_scores,
            'written_works_percentage': weighted_written_works_percentage,
            'performance_task_percentage': weighted_performance_task_percentage,
            'quarterly_assessment_percentage': weighted_quarterly_assessment_percentage,
        }

        return render(request, 'teacher_template/adviserTeacher/class_record.html', context)
    
    return render(request, 'teacher_template/adviserTeacher/home_adviser_teacher.html')


def calculate_grades(request):
    if request.method == "POST":
        print(request.POST)
        students = Student.objects.all()
        
        for student in students:
            scores_written_works = []
            scores_performance_task = []
            scores_quarterly_assessment = []

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
                written_works = request.POST.get(f"scores_written_{student.id}_{i}", "0")
                max_written_works = request.POST.get(f"max_written_works_{i}", "0")  # Change this to the actual maximum score
                performance_task = request.POST.get(f"scores_performance_task_{student.id}_{i}", "0")
                max_performance_task = request.POST.get(f"max_performance_task_{i}", "0")  # Change this to the actual maximum score
                # quarterly_assessment = request.POST.get(f"scores_quarterly_assessment_{student.id}_{i}", "0")
                # max_quarterly_assessment = request.POST.get(f"max_quarterly_assessment_{i}", "0")  # Change this to the actual maximum score
                
                # Retrieve weights for each component
                weight_input_written = float(request.POST.get(f"written_works_weight", "0"))  # Change this to the actual weight for written works
                weight_input_performance = float(request.POST.get(f"performance_task_weight", "0"))  # Change this to the actual weight for performance tasks
                # weight_input_quarterly = float(request.POST.get(f"weight_quarterly_assessment_{i}", "0"))  # Change this to the actual weight for quarterly assessments
                
                scores_written_works.append(float(written_works) if written_works.isnumeric() else 0)
                scores_performance_task.append(float(performance_task) if performance_task.isnumeric() else 0)
                # scores_quarterly_assessment.append(float(quarterly_assessment) if quarterly_assessment.isnumeric() else 0)

                total_score_written += float(written_works) if written_works.isnumeric() else 0
                total_max_score_written += float(max_written_works) if max_written_works.isnumeric() else 0
                total_score_performance += float(performance_task) if performance_task.isnumeric() else 0
                total_max_score_performance += float(max_performance_task) if max_performance_task.isnumeric() else 0
                # total_score_quarterly += float(quarterly_assessment) if quarterly_assessment.isnumeric() else 0
                # total_max_score_quarterly += float(max_quarterly_assessment) if max_quarterly_assessment.isnumeric() else 0

            # Perform your calculations (as in your original code)

            for i in range(1, 5):
                quarterly_assessment = request.POST.get(f"scores_quarterly_assessment_{student.id}_{i}", "0")
                max_quarterly_assessment = request.POST.get(f"max_quarterly_assessment_{i}", "0")  # Change this to the actual maximum score
                
                weight_input_quarterly = float(request.POST.get(f"quarterly_assessment_weight", "0"))  # Change this to the actual weight for quarterly assessments
                scores_quarterly_assessment.append(float(quarterly_assessment) if quarterly_assessment.isnumeric() else 0)
                total_score_quarterly += float(quarterly_assessment) if quarterly_assessment.isnumeric() else 0
                total_max_score_quarterly += float(max_quarterly_assessment) if max_quarterly_assessment.isnumeric() else 0

            if total_max_score_written > 0:
                percentage_score_written = (total_score_written / total_max_score_written) * 100
            else:
                percentage_score_written = 0

            if total_max_score_performance > 0:
                percentage_score_performance = (total_score_performance / total_max_score_performance) * 100
            else:
                percentage_score_performance = 0

            if total_max_score_quarterly > 0:
                percentage_score_quarterly = (total_score_quarterly / total_max_score_quarterly) * 100
            else:
                percentage_score_quarterly = 0

            weight_written = float(weight_input_written)
            weight_performance = float(weight_input_performance)
            weight_quarterly = float(weight_input_quarterly)

            weighted_score_written = (percentage_score_written / 100) * weight_written
            weighted_score_performance = (percentage_score_performance / 100) * weight_performance
            weighted_score_quarterly = (percentage_score_quarterly / 100) * weight_quarterly

            initial_grades = weighted_score_written + weighted_score_performance + weighted_score_quarterly
            transmuted_grades = transmuted_grade(initial_grades)

            # print(weight_input_written)
            # print(weight_input_performance)
            # print(weight_input_quarterly)

            # Create a new GradeScores object and populate its fields
            grade_scores = GradeScores(
                student_name=student.name,
                written_works_scores=scores_written_works,
                performance_task_scores=scores_performance_task,
                quarterly_assessment_scores=scores_quarterly_assessment,
                initial_grades=initial_grades,
                transmuted_grades=transmuted_grades,
                total_score_written=total_score_written,
                total_max_score_written=total_max_score_written,
                total_score_performance=total_score_performance,
                total_max_score_performance=total_max_score_performance,
                total_score_quarterly=total_score_quarterly,
                total_max_score_quarterly=total_max_score_quarterly,
                percentage_score_written=percentage_score_written,
                percentage_score_performance=percentage_score_performance,
                percentage_score_quarterly=percentage_score_quarterly,
                
                weighted_score_written=weighted_score_written,
                weighted_score_performance=weighted_score_performance,
                weighted_score_quarterly=weighted_score_quarterly,
            )

            # Save the GradeScores object to the database
            grade_scores.save()

        # Redirect to a success page or render a response as needed
        return redirect('display_classrecord')

    return render(request, "teacher_template/adviserTeacher/home_adviser_teacher.html")


def display_classrecord(request):
    grade_scores = GradeScores.objects.all()
    return render(request, 'teacher_template/adviserTeacher/display_classrecord.html', {'grade_scores': grade_scores})



@login_required
def display_students(request):
    user = request.user

    if user.user_type == 2:
        teacher = get_object_or_404(Teacher, user=user)
        students = Student.objects.filter(teacher=teacher)

        unique_grades = students.values_list('grade', flat=True).distinct()
        unique_sections = students.values_list('section', flat=True).distinct()

        context = {
            'teacher': teacher,
            'unique_grades_sections': zip(unique_grades, unique_sections),
        }
        return render(request, 'teacher_template/adviserTeacher/classes.html', context)

    return render(request, 'teacher_template/adviserTeacher/classes.html')

def student_list_for_class(request):
    grade = request.GET.get('grade')
    section = request.GET.get('section')
    
    # Fetch students based on grade and section
    students = Student.objects.filter(grade=grade, section=section)

    context = {
        'grade': grade,
        'section': section,
        'students': students,
    }

    return render(request, 'teacher_template/adviserTeacher/student_list.html', context)


