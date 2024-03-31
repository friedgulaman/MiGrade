from statistics import mean
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from CuyabSRMS.models import MT, AdvisoryClass,  ClassRecord, GeneralAverage, GradeScores, InboxMessage, QuarterlyGrades, Student, SuperAdmin, Admin, CustomUser, ActivityLog, Teacher
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST
from .utils import log_activity
import os
from dotenv import load_dotenv
import logging

# Create a logger
logger = logging.getLogger(__name__)
load_dotenv()

@login_required
def home_mt(request):
    mt_user = request.user

    try:
        mt_instance = MT.objects.get(user=mt_user)
        assigned_grades = [grade.strip() for grade in mt_instance.assigned_grades]

        matching_teachers = set()
        matching_keys = {}  # Use a dictionary to store key-value pairs

        for teacher in Teacher.objects.all():
            if teacher.grade_section:
                for key, value in teacher.grade_section.items():
                    if any(grade.lower() in key.lower() for grade in assigned_grades):
                        matching_teachers.add(teacher)
                        matching_keys[key] = value  # Add key-value pair to the dictionary

        context = {
            'matching_keys': matching_keys,
            'matching_teachers': matching_teachers,
        }

        return render(request, 'master_template/home_mt.html', context)
    
    except MT.DoesNotExist:
        pass
def advisory_classes_mt(request):
    # Get the current logged-in MT user
    mt_user = request.user

    try:
        # Retrieve the MT instance associated with the user
        mt_instance = MT.objects.get(user=mt_user)

        # Get the assigned grades of the MT user
        assigned_grades = mt_instance.assigned_grades

        # Initialize an empty set to store distinct grades
        distinct_grades = set()

        # Iterate through each assigned grade of the MT user
        for grade_name in assigned_grades:
            # Retrieve the class records matched to the assigned grade
            advisory = AdvisoryClass.objects.filter(grade=grade_name)

            # Extract distinct grades from the matching class records
            distinct_grades.update(advisory.values_list('grade', flat=True).distinct())

        context = {
            'distinct_grades': distinct_grades,
        }

        return render(request, 'master_template/advisory_classes.html', context)

    except MT.DoesNotExist:
        # Handle the case where the MT instance does not exist
        # Redirect or render an appropriate response
        pass


def advisory_sections(request):
    # Get the grade from the GET parameters
    grade = request.GET.get('grade')

    # Get the current logged-in MT user
    mt_user = request.user

    try:
        # Retrieve the MT instance associated with the user
        mt_instance = MT.objects.get(user=mt_user)

        # Get the assigned grades of the MT user
        assigned_grades = mt_instance.assigned_grades

        # Initialize an empty set to store distinct sections
        distinct_sections = set()

        # Check if the selected grade is among the assigned grades of the MT user
        if grade in assigned_grades:
            # Retrieve the class records matched to the selected grade
            class_records = ClassRecord.objects.filter(grade=grade)

            # Extract distinct sections from the matching class records
            distinct_sections = set(class_records.values_list('section', flat=True).distinct())

    except MT.DoesNotExist:
        # Handle the case where the MT instance does not exist
        # Redirect or render an appropriate response
        pass

    context = {
        'grade': grade,
        'distinct_sections': distinct_sections,
    }

    return render(request, 'master_template/advisory_sections.html', context)


def determine_remarks(general_average):
    if general_average is None:
        return 'No Grade'
     
    if general_average >= 98:
        return 'WITH HIGHEST HONOR'
    elif general_average >= 95:
        return 'WITH HIGH HONOR'
    elif general_average >= 90:
        return 'WITH HONOR'
    elif general_average >= 75:
        return 'PASSED'
    else:
        return 'FAILED'
    
def determine_status(general_average):
    if general_average is None:
        return 'No Grade'
     
    if general_average >= 98:
        return 'PASSED'
    elif general_average >= 95:
        return 'PASSED'
    elif general_average >= 90:
        return 'PASSED'
    elif general_average >= 75:
        return 'PASSED'
    else:
        return 'FAILED'


def save_general_average(student_data, grade, section):
    # Check if 'general_average' key is present in student_data and is not None
    if 'general_average' in student_data and student_data['general_average'] is not None:
        # Extract relevant information from student_data
        student = student_data['student']
        general_average = round(student_data['general_average'], 2)
        remarks = determine_remarks(general_average)
        status = determine_status(general_average)

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
            general_average_record.remarks = remarks
            general_average_record.status = status
            general_average_record.save()
        else:
            # Create a new record if none exist
            GeneralAverage.objects.create(
                student=student,
                grade=grade,
                section=section,
                general_average=general_average,
                remarks=remarks,
                status=status
            )
@login_required
def advisory_summary(request):
    # Get the current logged-in MT user
    mt_user = request.user

    try:
        # Retrieve the MT instance associated with the user
        mt_instance = MT.objects.get(user=mt_user)

        # Get parameters from the request
        grade = request.GET.get('grade')
        section = request.GET.get('section')
        class_type = request.GET.get('class_type')
        quarter = request.GET.get('quarter', '1st Quarter')  # Default to 1st Quarter if not provided

        # Fetch advisory classes based on teacher, grade, and section
        advisory_classes = AdvisoryClass.objects.filter(grade=grade, section=section)

        unique_keys = set()  # Initialize an empty set here

        if advisory_classes.exists():
            for advisory_class in advisory_classes:
                grades_data = advisory_class.grades_data
                if grades_data:
                    for key, value in grades_data.items():
                        unique_keys.add((key, value.get('from_teacher_id')))  # Add (key, from_teacher_id) tuple to the set

        else:
            print("No AdvisoryClass objects found for the specified criteria")

        # Filter students based on the class type
        students = Student.objects.filter(grade=grade, section=section)
        students_filtered = []
        for student in students:
            class_type_json = student.class_type
            if class_type_json and str(mt_user.id) in class_type_json and class_type_json[str(mt_user.id)] == class_type:
                students_filtered.append(student)

        # Unique keys context
        unique_keys_context = list(unique_keys)

        # Filter quarterly grades based on the selected quarter
        quarterly_grades = QuarterlyGrades.objects.filter(student__grade=grade, student__section=section, quarter=quarter)

        # Prepare data to pass to the template
        data = []
        for index, grades in enumerate(quarterly_grades, start=1):
            student_name = grades.student.name
            subjects_grades = grades.grades
            average_score = subjects_grades.pop('average_score', None)
            subjects_data = [{'subject': subject, 'score': score} for subject, score in subjects_grades.items()]

            data.append({
                'no': index,
                'student_name': student_name,
                'subjects_data': subjects_data,
                'average_score': average_score,
            })

        students = AdvisoryClass.objects.filter(grade=grade, section=section)

        # Dictionary to store subject-wise grades and average score for each student
        subject_grades = {}
        quarter_mapping = {
            '1st Quarter': 'first_quarter',
            '2nd Quarter': 'second_quarter',
            '3rd Quarter': 'third_quarter',
            '4th Quarter': 'fourth_quarter',
        }

        # Fetch subject-wise grades for each student
        for student in students:
            grades_data = student.grades_data
            subject_grades[student.student.name] = {}
            grades = []  # List to store grades for calculating mean

            for subject, grades_info in grades_data.items():
                # Skip subjects 'MUSIC', 'ARTS', 'PE', and 'HEALTH'
                if subject in ['MUSIC', 'ARTS', 'PE', 'HEALTH']:
                    continue
                
                if quarter_mapping[quarter] in grades_info:
                    subject_grade = grades_info[quarter_mapping[quarter]]
         
                    subject_grade_str = str(subject_grade) if subject_grade is not None else ""
                    if subject_grade_str.strip():  # Check if the string is not empty after stripping whitespace
                        subject_grades[student.student.name][subject] = subject_grade_str
                        if subject_grade is not None:
                            grades.append(float(subject_grade))

            # Calculate average score
            if grades:
                subject_grades[student.student.name]['average_score'] = round(mean(grades), 2)
            else:
                subject_grades[student.student.name]['average_score'] = ""

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

        subjects = list(students.first().grades_data.keys()) if students else []

        students = Student.objects.filter(grade=grade, section=section)
        advisory_classes = AdvisoryClass.objects.filter(grade=grade, section=section)

        final_grades = []
        for student in students:
            student_data = {
                'id': student.id,
                'name': student.name,
                'grade': grade,
                'section': section,
                'subjects': [],
                'student': student
            }

            for advisory_class in advisory_classes.filter(student=student):
                grades_data = advisory_class.grades_data
                for subject, subject_info in grades_data.items():
                    if subject.upper() in ['MUSIC', 'ARTS', 'PE', 'HEALTH']:
                        continue
                    # Access grades data for each subject
                    subject_data = {
                        'subject': subject,
                        'quarter_grades': {
                            'first_quarter': subject_info.get('first_quarter', ''),
                            'second_quarter': subject_info.get('second_quarter', ''),
                            'third_quarter': subject_info.get('third_quarter', ''),
                            'fourth_quarter': subject_info.get('fourth_quarter', ''),
                            # Add more quarters if available
                        },
                        'final_grade': subject_info.get('final_grade', ''),
                        'teacher_name': subject_info.get('from_teacher_id', 'Unknown Teacher')
                    }
                    student_data['subjects'].append(subject_data)

            # Append student data to the final grades
            final_grades.append(student_data)
        
        # Compute the general average and save it for each student
        for student_data in final_grades:
            total_final_grade = 0
            num_subjects = len(student_data['subjects'])
            for subject_info in student_data['subjects']:
                final_grade = subject_info['final_grade']
                try:    
                    if final_grade is not None:
                        total_final_grade += float(final_grade) 
                except ValueError:
                    # Handle the case where final_grade is not a valid number
                    pass

            student_data['general_average'] = total_final_grade / num_subjects if num_subjects > 0 else 0
            save_general_average(student_data, grade, section)

        sorted_final_grades = sorted(final_grades, key=lambda x: x.get('general_average', 0), reverse=True)

        highest_per_quarter = {
            'first_quarter': [],
            'second_quarter': [],
            'third_quarter': [],
            'fourth_quarter': [],
        }

        # Populate data for each quarter
        for quarters in ['first_quarter', 'second_quarter', 'third_quarter', 'fourth_quarter']:
            sorted_students = []
            for student in final_grades:
                if 'subjects' in student and student['subjects']:  # Check if 'subjects' list exists and is not empty
                    quarter_grades = student['subjects'][0]['quarter_grades'].get(quarters)
                    if quarter_grades is not None and quarter_grades != '':
                        sorted_students.append(student)
            sorted_students = sorted(sorted_students, key=lambda x: float(x['subjects'][0]['quarter_grades'].get(quarters, '0') or '0'), reverse=True)
            highest_per_quarter[quarters] = sorted_students

        general_averages = GeneralAverage.objects.filter(grade=grade, section=section)

        # Sort GeneralAverage instances based on the general average from highest to lowest
        sorted_general_averages = general_averages.order_by('-general_average')

        # Filter class records based on the teacher
        class_records = AdvisoryClass.objects.filter(grade=grade, section=section)

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
            'grade': grade,
            'section': section,
            'unique_keys': unique_keys_context,
            'students': students_filtered,
            'class_type': class_type,
            'data': data,
            'quarter': quarter,
            'final_grades': sorted_final_grades,
            'highest_per_quarter': highest_per_quarter,
            'general_averages': sorted_general_averages,
            'class_records': unique_class_records,
        }

        return render(request, 'master_template/advisory_summary.html', context)

    except MT.DoesNotExist:
        # Handle the case where the MT instance does not exist
        # Redirect or render an appropriate response
        pass

def subject_classes_mt(request):
    # Get the current logged-in MT user
    mt_user = request.user

    try:
        # Retrieve the MT instance associated with the user
        mt_instance = MT.objects.get(user=mt_user)

        # Get the assigned grades of the MT user
        assigned_grades = mt_instance.assigned_grades

        # Initialize an empty set to store distinct grades
        distinct_grades = set()

        # Iterate through each assigned grade of the MT user
        for grade_name in assigned_grades:
            # Retrieve the class records matched to the assigned grade
            class_records = ClassRecord.objects.filter(grade=grade_name)

            # Extract distinct grades from the matching class records
            distinct_grades.update(class_records.values_list('grade', flat=True).distinct())

        context = {
            'distinct_grades': distinct_grades,
        }

        return render(request, 'master_template/subject_classes.html', context)
    
    except MT.DoesNotExist:
        # Handle the case where the MT instance does not exist
        # Redirect or render an appropriate response
        pass

def distinct_sections(request):
    # Get the grade from the GET parameters
    grade = request.GET.get('grade')

    # Get the current logged-in MT user
    mt_user = request.user

    try:
        # Retrieve the MT instance associated with the user
        mt_instance = MT.objects.get(user=mt_user)

        # Get the assigned grades of the MT user
        assigned_grades = mt_instance.assigned_grades

        # Initialize an empty set to store distinct sections
        distinct_sections = set()

        # Check if the selected grade is among the assigned grades of the MT user
        if grade in assigned_grades:
            # Retrieve the class records matched to the selected grade
            class_records = ClassRecord.objects.filter(grade=grade)

            # Extract distinct sections from the matching class records
            distinct_sections = set(class_records.values_list('section', flat=True).distinct())

    except MT.DoesNotExist:
        # Handle the case where the MT instance does not exist
        # Redirect or render an appropriate response
        pass

    context = {
        'grade': grade,
        'distinct_sections': distinct_sections,
    }

    return render(request, 'master_template/subject_sections.html', context)

def subject_subjects(request):
    # Get the section from the GET parameters
    grade = request.GET.get('grade')
    section = request.GET.get('section')

    # Get the current logged-in MT user
    mt_user = request.user

    try:
        # Retrieve the MT instance associated with the user
        mt_instance = MT.objects.get(user=mt_user)

        # Get the assigned grades of the MT user
        assigned_grades = mt_instance.assigned_grades

        # Initialize an empty list to store quarters
        subjects = []

        # Iterate through each assigned grade of the MT user
        for grade_name in assigned_grades:
            # Retrieve the class records matched to the grade and section
            class_records = ClassRecord.objects.filter(grade=grade_name, section=section)

            # Extract distinct subjects from the matching class records
            subjects.extend(class_records.values_list('subject', flat=True).distinct())

    except MT.DoesNotExist:
        # Handle the case where the MT instance does not exist
        # Redirect or render an appropriate response
        pass

    context = {
        'grade': grade,
        'section': section,
        'subjects': subjects,
    }

    return render(request, 'master_template/subject_subjects.html', context)

def subject_quarters(request):
    grade = request.GET.get('grade')
    # Get the section from the GET parameters
    section = request.GET.get('section')
    subject = request.GET.get('subject')

    # Get the current logged-in MT user
    mt_user = request.user

    try:
        # Retrieve the MT instance associated with the user
        mt_instance = MT.objects.get(user=mt_user)

        # Get the assigned grades of the MT user
        assigned_grades = mt_instance.assigned_grades

        # Initialize an empty list to store quarters
        quarters = []

        # Iterate through each assigned grade of the MT user
        for grade_name in assigned_grades:
            # Retrieve the class records matched to the grade and section
            class_records = ClassRecord.objects.filter(grade=grade_name, section=section, subject=subject)

            # Extract distinct subjects from the matching class records
            quarters.extend(class_records.values_list('quarters', flat=True).distinct())

    except MT.DoesNotExist:
        # Handle the case where the MT instance does not exist
        # Redirect or render an appropriate response
        pass

    context = {
        'grade': grade,
        'section': section,
        'subject': subject,
        'quarters': quarters,
    }

    return render(request, 'master_template/subject_quarters.html', context)

def summary_per_quarter(request):
    grade = request.GET.get('grade')
    # Get the section from the GET parameters
    section = request.GET.get('section')
    subject = request.GET.get('subject')
    quarter = request.GET.get('quarter')

     # Retrieve the specific class record based on the provided class_record_id
    class_record = get_object_or_404(ClassRecord, grade=grade, section=section, subject=subject, quarters=quarter)

    # Retrieve grade scores related to the class record
    grade_scores = GradeScores.objects.filter(class_record=class_record)

    # Handle None values for initial_grades and transmuted_grades
    for grade_score in grade_scores:
        if grade_score.initial_grades is None:
            grade_score.initial_grades = ""
        if grade_score.transmuted_grades is None:
            grade_score.transmuted_grades = ""

    context = {
        'subject': subject,
        'quarter': quarter,
        'class_record': class_record,
        'grade_scores': grade_scores,
    }


    return render(request, 'master_template/subject_summary.html', context)