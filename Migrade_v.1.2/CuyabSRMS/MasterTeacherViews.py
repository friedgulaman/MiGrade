from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from CuyabSRMS.models import MT, AdvisoryClass, ApprovedMessage, ClassRecord, InboxMessage, SuperAdmin, Admin, CustomUser, ActivityLog, Teacher
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

def inbox_open_mt(request):
    try:
        user = request.user

        # Check if the logged-in user is a teacher
        if hasattr(user, 'mt'):
            mt = user.mt.id
            print(mt)
            # Get inbox messages where the logged-in mt is the intended recipient
            inbox_messages = InboxMessage.objects.all()
            approved_messages = ApprovedMessage.objects.filter(approved_by_id=mt)

            context = {
                'inbox_messages': inbox_messages,
                'approved_messages': approved_messages
            }
            return render(request, 'master_template/inbox_mt.html', context)

        else:
            # Handle the case where the logged-in user is not a mt
            return render(request, 'master_template/inbox_mt.html', {'inbox_messages': []})

    except Exception as e:
        # Handle any exceptions
        print(f"Error in inbox_open: {e}")
        return render(request, 'master_template/inbox_mt.html', {'inbox_messages': []})




@login_required
def accept_message_mt(request):
    if request.method == 'POST':
        message_id = request.POST.get('message_id')
        try:
            # Retrieve the InboxMessage object
            message = InboxMessage.objects.get(pk=message_id)
            # Update the accepted field to True
            message.approved = True
            # Set the approved_by field to the current MT user
            message.approved_by = MT.objects.get(user=request.user)
            message.save()
            
            # Retrieve the appropriate Teacher instance for the to_teacher field
            # This assumes you have a way to determine the correct Teacher instance based on your application logic
            to_teacher = Teacher.objects.get(pk=message.to_teacher)

            # Create an ApprovedMessage object and save approved message data
            ApprovedMessage.objects.create(
                message_id=message_id,
                file_name=message.file_name,
                json_data=message.json_data,
                approved_by=message.approved_by,
                to_teacher=to_teacher  # Assign the Teacher instance to the to_teacher field
            )
            
            return JsonResponse({'success': True, 'message': 'Message accepted successfully.'})
        except InboxMessage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Message not found.'})
        except MT.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'MT user not found.'})
        except Teacher.DoesNotExist:  # Handle the case where the Teacher instance is not found
            return JsonResponse({'success': False, 'error': 'Teacher not found.'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

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
        'section': section,
        'subjects': subjects,
    }

    return render(request, 'master_template/subject_subjects.html', context)

def subject_quarters(request):
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
        'section': section,
        'subject': subject,
        'quarters': quarters,
    }

    return render(request, 'master_template/subject_quarters.html', context)