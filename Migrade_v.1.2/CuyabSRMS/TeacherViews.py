import json
import os

import io
import re

from CuyabSRMS.utils import transmuted_grade
from CuyabSRMS import StudentViews
from django import forms
import openpyxl
from django.contrib import messages
from django.shortcuts import render
from .models import Grade, GradeScores, Section, Student, Teacher
from django.contrib.auth import get_user_model  # Add this import statement
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect

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


def home_teacher(request):
    return render(request, 'teacher_template/home_teacher.html')


# adviser
def home_adviser_teacher(request):
    return render(request, 'teacher_template/adviserTeacher/home_adviser_teacher.html')

def upload_adviser_teacher(request):
    return render(request, 'teacher_template/adviserTeacher/upload.html')

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


def upload(request):
    if request.method == 'POST':
        google_sheet_link = request.POST.get('google_sheet_link')

        # Extract the spreadsheet ID from the Google Sheet link using regular expression
        spreadsheet_id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', google_sheet_link)
        
        if spreadsheet_id_match:
            spreadsheet_id = spreadsheet_id_match.group(1)

            # Extract the sheet name if available
            sheet_name_match = re.search(r'#gid=([0-9]+)', google_sheet_link)
            sheet_name = sheet_name_match.group(1) if sheet_name_match else None

            # Process the Google Sheet using your existing code
            lrn_data = process_google_sheet(spreadsheet_id, sheet_name)

            if lrn_data is not None:
                return render(request, 'teacher_template/adviserTeacher/upload.html', {
                    'lrn_data': lrn_data,
                })
            else:
                return HttpResponse("Failed to process the Google Sheet")
        else:
            return HttpResponse("Invalid Google Sheet link")

    # Render the initial form if the request is not a POST or if there are form errors
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

def new_classrecord(request):
        return render(request, 'teacher_template/adviserTeacher/new_classrecord.html')

def class_record(request):
    students = Student.objects.all()  # Replace with your actual query

    context = {
        'students': students,
    }
    
    return render(request, 'teacher_template/adviserTeacher/class_record.html', context)


def get_grade_details(request):
    grades = Student.objects.values_list('grade', flat=True).distinct()
    sections = Student.objects.values_list('section', flat=True).distinct()

    context = {
        'grades': grades,
        'sections': sections,
    }
    print("Distinct grades:", grades)
    print("Distinct sections:", sections)

    return render(request, 'teacher_template/adviserTeacher/new_classrecord.html', context)

# views.py
def get_students_by_grade_and_section(request):
    if request.method == "POST":
        grade_name = request.POST.get("grade")
        section_name = request.POST.get("section")

        # Query the database to retrieve students based on the selected grade and section
        students = Student.objects.filter(grade=grade_name, section=section_name)

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
                quarterly_assessment = request.POST.get(f"scores_quarterly_assessment_{student.id}_{i}", "0")
                max_quarterly_assessment = request.POST.get(f"max_quarterly_assessment_{i}", "0")  # Change this to the actual maximum score
                
                # Retrieve weights for each component
                weight_input_written = float(request.POST.get(f"weight_written_works_{i}", "0"))  # Change this to the actual weight for written works
                weight_input_performance = float(request.POST.get(f"weight_performance_task_{i}", "0"))  # Change this to the actual weight for performance tasks
                weight_input_quarterly = float(request.POST.get(f"weight_quarterly_assessment_{i}", "0"))  # Change this to the actual weight for quarterly assessments
                
                scores_written_works.append(float(written_works) if written_works.isnumeric() else 0)
                scores_performance_task.append(float(performance_task) if performance_task.isnumeric() else 0)
                scores_quarterly_assessment.append(float(quarterly_assessment) if quarterly_assessment.isnumeric() else 0)

                total_score_written += float(written_works) if written_works.isnumeric() else 0
                total_max_score_written += float(max_written_works) if max_written_works.isnumeric() else 0
                total_score_performance += float(performance_task) if performance_task.isnumeric() else 0
                total_max_score_performance += float(max_performance_task) if max_performance_task.isnumeric() else 0
                total_score_quarterly += float(quarterly_assessment) if quarterly_assessment.isnumeric() else 0
                total_max_score_quarterly += float(max_quarterly_assessment) if max_quarterly_assessment.isnumeric() else 0

            # Perform your calculations (as in your original code)

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

            weighted_score_written = (percentage_score_written * weight_written) / 100
            weighted_score_performance = (percentage_score_performance * weight_performance) / 100
            weighted_score_quarterly = (percentage_score_quarterly * weight_quarterly) / 100

            initial_grades = weighted_score_written + weighted_score_performance + weighted_score_quarterly
            transmuted_grades = transmuted_grade(initial_grades)

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






# Subject teacher
def home_subject_teacher(request):
    return render(request, 'teacher_template/subjectTeacher/home_subject_teacher.html')

def filipino_subject(request):
    return render (request, 'teacher_template/subjectTeacher/filipino_subject.html')

