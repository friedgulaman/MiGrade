from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from CuyabSRMS.models import MT, AdvisoryClass,  ClassRecord, InboxMessage, SuperAdmin, Admin, CustomUser, ActivityLog, Teacher
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
    # Get the current logged-in MT user
    mt_user = request.user

    try:
        # Retrieve the MT instance associated with the user
        mt_instance = MT.objects.get(user=mt_user)

        # Get the assigned grades of the MT user
        assigned_grades = mt_instance.assigned_grades

        # Initialize empty sets to store matching teachers, class records, and advisory classes
        matching_teachers = set()
        matching_class_records = set()
        matching_advisory_classes = set()

        # Iterate through each assigned grade of the MT user
        for grade_name in assigned_grades:
            # Retrieve the teachers who handle the assigned grade
            teachers = Teacher.objects.filter(grade_section__has_key=grade_name)
            
            # Filter the teachers to include only those with matching assigned grades
            for teacher in teachers:
                if grade_name in teacher.grade_section:
                    matching_teachers.add(teacher)

            # Retrieve the class records matched to the assigned grade
            class_records = ClassRecord.objects.filter(grade=grade_name)
            matching_class_records.update(class_records)

            # Retrieve the advisory classes whose grade matches the assigned grade
            advisory_classes = AdvisoryClass.objects.filter(grade=grade_name)
            matching_advisory_classes.update(advisory_classes)

        context = {
            'matching_teachers': matching_teachers,
            'matching_class_records': matching_class_records,
            'matching_advisory_classes': matching_advisory_classes,
            'assigned_grades': assigned_grades,
        }

        return render(request, 'master_template/home_mt.html', context)
    
    except MT.DoesNotExist:
        # Handle the case where the MT instance does not exist
        # Redirect or render an appropriate response
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