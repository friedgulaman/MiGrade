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
from .models import Grade, GradeScores, Section, Student, Teacher, Subject, Quarters, ClassRecord
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
from .views import *
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm


#Grade
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .forms import GradeScoresForm


@login_required

def home_teacher(request):
    return render(request, 'teacher_template/home_teacher.html')

def upload_adviser_teacher(request):
    return render(request, 'teacher_template/adviserTeacher/upload.html')

def new_classrecord(request):
        return render(request, 'teacher_template/adviserTeacher/new_classrecord.html')

def classes(request):
        return render(request, 'teacher_template/adviserTeacher/classes.html')


# adviser
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
            print(lrn_data)

            if lrn_data is not None:
                return render(request, 'teacher_template/adviserTeacher/upload.html', {
                    'lrn_data': lrn_data,
                })
            else:
                messages.error(request, "Failed to process the Google Sheet")
        else:
            messages.error(request, "Invalid Google Sheet link")

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

# views.py
def get_students_by_grade_and_section(request):
    if request.method == "POST":
        grade_name = request.POST.get("grade")
        section_name = request.POST.get("section")
        subject_name = request.POST.get("subject")
        quarter_name = request.POST.get("quarter")
        # teacher_id = request.POST.get("teacher")

        user = request.user

        teacher = get_object_or_404(Teacher, user=user)
        teacher_identifier = str(teacher)

        classrecord = ClassRecord(
            name= grade_name + section_name + subject_name + quarter_name,
            grade=grade_name,
            section=section_name,
            subject=subject_name,
            quarters=quarter_name,
            teacher=teacher,  # Assign the Teacher instance, not the ID
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
            scores = GradeScores.objects.filter(student_name=student_name)

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
        scores_qa_hps = [request.POST.get(f"max_quarterly_assessment_{i}") for i in range(1, 5)]
        total_ww_hps = request.POST.get("total_max_written_works")
        total_pt_hps = request.POST.get("total_max_performance_task")
        total_qa_hps = request.POST.get("total_max_quarterly")
        weight_written= request.POST.get("written_works_weight")
        weight_performance= request.POST.get("performance_task_weight")
        weight_quarterly= request.POST.get("quarterly_assessment_weight")

        print(scores_pt_hps)
        print(scores_qa_hps)
        print(scores_ww_hps)

        class_record = ClassRecord.objects.get(grade=grade_name, section=section_name, subject=subject_name, quarters=quarters_name)
        # subject_name = request.POST.get("subject")
        # quarter_name = request.POST.get("quarter")
        

        students = Student.objects.filter(grade=grade_name, section=section_name)
        
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
                quarterly_assessment = request.POST.get(f"scores_quarterly_assessment_{student.id}_{i}")
                max_quarterly_assessment = request.POST.get(f"max_quarterly_assessment_{i}")  # Change this to the actual maximum score
                
                weight_input_quarterly = float(request.POST.get(f"quarterly_assessment_weight"))  # Change this to the actual weight for quarterly assessments
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


            # Create a new GradeScores object and populate its fields
            grade_scores = GradeScores(
                student_name=student.name,
                class_record=class_record,
                scores_hps_written=scores_ww_hps,
                scores_hps_performance=scores_pt_hps,
                scores_hps_quarterly=scores_qa_hps,
                total_ww_hps=total_ww_hps,
                total_qa_hps=total_qa_hps,
                total_pt_hps=total_pt_hps,
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
    # Get the currently logged-in user
    user = request.user

    if user.user_type == 2:
        try:
            # Retrieve the teacher associated with the user
            teacher = Teacher.objects.get(user=user)
            
            # Filter students based on the teacher
            students = Student.objects.filter(teacher=teacher)

            # You can also filter students by grade and section if needed
            grade = request.GET.get('grade')  # Example: Get grade from request
            section = request.GET.get('section')  # Example: Get section from request

            if grade and section:
                students = students.filter(grade=grade, section=section)

            # Extract unique grades and sections from the students
            unique_grades = students.values_list('grade', flat=True).distinct()
            unique_sections = students.values_list('section', flat=True).distinct()

            context = {
                'students': students,
                'teacher': teacher,
                'unique_grades': unique_grades,  # Pass unique grades to the template
                'unique_sections': unique_sections,  # Pass unique sections to the template
                'grade': grade,
                'section': section,
            }
            return render(request, 'teacher_template/adviserTeacher/classes.html', context)
        except Teacher.DoesNotExist:
            # Handle the case where the user has user_type=2 but is not associated with a teacher
            return render(request, 'teacher_template/adviserTeacher/classes.html')
    else:
        # Handle the case where the user is not a teacher (user_type is not 2)
        return render(request, 'teacher_template/adviserTeacher/classes.html')

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


def display_quarterly_summary(request, grade, section, subject):
    class_records = ClassRecord.objects.filter(grade=grade, section=section, subject=subject)
    
    quarterly_summaries = []
    for class_record in class_records:
        grade_scores = GradeScores.objects.filter(class_record=class_record)
        quarterly_summaries.append({
            'class_record': class_record,
            'grade_scores': grade_scores,
        })

    context = {
        'quarterly_summaries': quarterly_summaries,
    }

    return render(request, "teacher_template/adviserTeacher/summary_of_quarterly_grade.html", context)

def display_final_grades(request, grade, section):
    students = Student.objects.filter(grade=grade, section=section)
    subjects = ClassRecord.objects.filter(grade=grade, section=section).values('subject').distinct()
    quarters = ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter']

    final_grades = []
    for student in students:
        student_data = {'id': student.id, 'name': student.name, 'grade': grade, 'section': section, 'subjects': []}

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
                    student_name=student.name
                ).first()

                subject_info['quarter_grades'][quarter] = grade_score.initial_grades if grade_score else 0

            # Calculate the final grade for the subject
            subject_info['final_grade'] = sum(subject_info['quarter_grades'].values()) / len(subject_info['quarter_grades']) \
                if len(subject_info['quarter_grades']) > 0 else 0

            student_data['subjects'].append(subject_info)

        # Append student data to the final grades
        final_grades.append(student_data)

    context = {
        'grade': grade,
        'section': section,
        'final_grades': final_grades,
    }


    return render(request, "teacher_template/adviserTeacher/final_grades.html", context)


def update_score(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        student_name = request.POST.get('student_name')
        new_score = request.POST.get('new_score')
        column_index = int(request.POST.get('column_index'))
        section_id = request.POST.get('section_id')  # Added section_id for differentiation
        class_record_id = request.POST.get('class_record_id')
        scores_hps_data = request.POST.getlist('scores_hps[]')  # Retrieve scores_hps data as a list

        print("Request POST Data:", request.POST)
        print("Class Record ID:", class_record_id)
        print("Scores HPS Data:", scores_hps_data)  # Add this line for debugging

        try:
            # Retrieve the GradeScores object based on student name and class record id
            grade_score = GradeScores.objects.get(
                student_name=student_name,
                class_record__id=class_record_id
            )

            print("Grade Score Found:", grade_score)  # Add this line for debugging
        except GradeScores.DoesNotExist:
            print(f"Not Found: /update_score/")
            return HttpResponse("GradeScores not found for the given student and class record ID.", status=404)
  # Add this line for debugging

        # Determine the field to update based on the section_id
        if section_id == 'written_works':
            scores_field = 'written_works_scores'
            total_field = 'total_score_written'
            percentage_field = 'percentage_score_written'
            weighted_field = 'weighted_score_written'
            hps_field = 'scores_hps_written'  # Adjust with your actual field name for HPS
        elif section_id == 'performance_task':
            scores_field = 'performance_task_scores'
            total_field = 'total_score_performance'
            percentage_field = 'percentage_score_performance'
            weighted_field = 'weighted_score_performance'
            hps_field = 'scores_hps_performance'  # Adjust with your actual field name for HPS
        elif section_id == 'quarterly_assessment':
            scores_field = 'quarterly_assessment_scores'
            total_field = 'total_score_quarterly'
            percentage_field = 'percentage_score_quarterly'
            weighted_field = 'weighted_score_quarterly'
            hps_field = 'scores_hps_quarterly'  # Adjust with your actual field name for HPS
        else:
            return JsonResponse({'error': 'Invalid section_id'})

        # Update the specific value in the scores list
        scores_list = list(map(int, getattr(grade_score, scores_field)))
        scores_list[column_index] = int(new_score)
        setattr(grade_score, scores_field, scores_list)

        # Update HPS data
        hps_list = [int(float(score)) for score in scores_hps_data]
        setattr(grade_score, hps_field, hps_list)

        # Recalculate total_score, percentage_score, and weighted_score
        setattr(grade_score, total_field, sum(scores_list))
        setattr(grade_score, percentage_field, (getattr(grade_score, total_field) / 100) * 100)
        setattr(grade_score, weighted_field, getattr(grade_score, percentage_field) * 0.2)

        grade_score.save()

        # Return updated data as JSON response
        response_data = {
            'total_score': getattr(grade_score, total_field),
            'percentage_score': getattr(grade_score, percentage_field),
            'weighted_score': getattr(grade_score, weighted_field),
            'scores_hps': getattr(grade_score, hps_field),
        }

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request'})


def update_highest_possible_scores(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        class_record_id = request.POST.get('class_record_id')
        section_id = request.POST.get('section_id')
        new_hps_data = request.POST.getlist('new_hps_data[]')

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
            new_hps_list = [float(value) if value != '' else 0.0 for value in new_hps_data]

            # Update the scores_hps field with the new list
            setattr(grade_score, hps_field, new_hps_list)
            grade_score.save()

            # Update the total_hps_field
            total_hps_value = sum(new_hps_list)
            setattr(grade_score, total_hps_field, total_hps_value)
            grade_score.save()

        return JsonResponse({'success': True})

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