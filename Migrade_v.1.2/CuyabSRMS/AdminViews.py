from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import MT, ActivityLog, Announcement, CustomUser, Quarters, SchoolInformation, Student, Teacher, Grade, Section
from .models import Announcement, CustomUser, Quarters, Student, Teacher, Grade, Section, SchoolInformation
from .models import ActivityLog, Announcement, CustomUser, Quarters, SchoolInformation, Student, Teacher, Grade, Section
from .models import Announcement, CustomUser, Quarters, Student, Teacher, Grade, Section, SchoolInformation, ArchivedClassRecord, ArchivedStudent, CoreValues, BehaviorStatement
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.db import models
from django.views.decorators.http import require_GET
from django.db.models import Q
from .forms import SubjectForm, CoreValuesForm, BehaviorStatementForm
from .models import Subject
from .views import log_activity
#OCR
from .models import ExtractedData
from .models import ProcessedDocument
from google.cloud import documentai_v1beta3 as documentai
from django.core.paginator import Paginator
import re
import os
import json
from .forms import DocumentUploadForm
from django.conf import settings
from django.shortcuts import HttpResponse
from django.utils.text import get_valid_filename
from .forms import ExtractedDataForm, SchoolInformationForm, DocumentBatchUploadForm

import openpyxl
from django.utils import timezone
import datetime
from datetime import datetime
from dateutil import parser
import pandas as pd
from google.api_core.client_options import ClientOptions

from django.db.models import Value
from django.db.models.functions import Cast


import io
from openpyxl import Workbook
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import escape_uri_path
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
import base64

from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import os
from dotenv import load_dotenv
import logging


logger = logging.getLogger(__name__)
load_dotenv()

@login_required
def manage_master_teacher(request):
        masters = MT.objects.all()
        return render(request, 'admin_template/manage_master.html', {'masters': masters})

@login_required
def assign_master(request):
    all_grades = Grade.objects.all()
    assigned_grades = set()

    for mt in MT.objects.all():
        assigned_grades.update(mt.assigned_grades)

    unassigned_grades = [grade for grade in all_grades if grade.name not in assigned_grades]

    context = {
        'grades': unassigned_grades,
        'masters': MT.objects.all(),
    }
    return render(request, 'admin_template/assign_master.html', context)


@login_required
def save_assignment(request):
    if request.method == 'POST':
        master_id = request.POST.get('master')
        grade_id = request.POST.get('grade')

        if master_id and grade_id:
            try:
                master = get_object_or_404(MT, id=master_id)
                grade = get_object_or_404(Grade, id=grade_id)
                
                assigned_grades = master.assigned_grades or []
                assigned_grades.append(grade.name)
                master.assigned_grades = assigned_grades
                master.save()

                messages.success(request, 'Assignment saved successfully')
                return JsonResponse({'success': True})
            except MT.DoesNotExist or Grade.DoesNotExist:
                messages.error(request, 'Invalid master or grade')
        else:
            messages.error(request, 'Invalid data')
    else:
        messages.error(request, 'Invalid request method')

    return JsonResponse({'success': False})

@login_required
@require_POST
def remove_grade(request):
    master_id = request.POST.get('master_id')
    grade_name = request.POST.get('grade')

    master = get_object_or_404(MT, id=master_id)

    if grade_name in master.assigned_grades:
        master.assigned_grades.remove(grade_name)
        master.save()
        messages.success(request, f'Grade "{grade_name}" removed from master successfully.')
    else:
        messages.error(request, f'Grade "{grade_name}" is not assigned to this master.')

    return redirect('assign_master')
    
def add_master(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('home_mt')
    else:
        default = os.getenv("MT")
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        middle_ini = request.POST.get('middle_ini')
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password', default)
        user = request.user

        try:
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                middle_ini=middle_ini,
                user_type=4, 
            )
            logger.debug('Admin added successfully!')
            return JsonResponse({'success': True, 'message': 'Admin Added Successfully!'})
        except IntegrityError as e:
            logger.exception('Failed to add Admin: %s', e)
            messages.error(request, "Failed to Add Admin!")

            return JsonResponse({'success': False, 'message': 'Failed to Add Admin!'})

@login_required
def create_core_values(request):
    if request.method == 'POST':
        form = CoreValuesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('display_core_values')
    else:
        form = CoreValuesForm()
    return render(request, 'admin_template/create_core_values.html', {'form': form})

@login_required
def display_core_values(request):
    core_values = CoreValues.objects.all()
    return render(request, 'admin_template/display_core_values.html', {'core_values': core_values})

@login_required
def update_core_values(request, core_values_id):
    core_values = get_object_or_404(CoreValues, pk=core_values_id)
    if request.method == 'POST':
        form = CoreValuesForm(request.POST, instance=core_values)
        if form.is_valid():
            form.save()
            return redirect('display_core_values')
    else:
        form = CoreValuesForm(instance=core_values)
    
    return render(request, 'admin_template/update_core_values.html', {'form': form, 'core_values': core_values})

@login_required
def delete_core_values(request, core_values_id):
    core_values = get_object_or_404(CoreValues, pk=core_values_id)
    if request.method == 'POST':
        core_values.delete()
        return redirect('display_core_values')

    return render(request, 'admin_template/delete_core_values.html', {'core_values': core_values})

@login_required
def create_behavior_statements(request):
    if request.method == 'POST':
        form = BehaviorStatementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('display_behavior_statements')
    else:   
        form = BehaviorStatementForm()
    return render(request, 'admin_template/create_behavior_statements.html', {'form': form})

@login_required
def display_behavior_statements(request):
    behavior_statements = BehaviorStatement.objects.all()
    return render(request, 'admin_template/display_behavior_statements.html', {'behavior_statements': behavior_statements})

@login_required
def update_behavior_statement(request, behavior_statement_id):
    behavior_statement = get_object_or_404(BehaviorStatement, pk=behavior_statement_id)
    if request.method == 'POST':
        form = BehaviorStatementForm(request.POST, instance=behavior_statement)
        if form.is_valid():
            form.save()
            return redirect('display_behavior_statements')
    else:
        form = BehaviorStatementForm(instance=behavior_statement)
    return render(request, 'admin_template/update_behavior_statement.html', {'form': form, 'behavior_statement': behavior_statement})

@login_required
def delete_behavior_statement(request, behavior_statement_id):
    behavior_statement = get_object_or_404(BehaviorStatement, pk=behavior_statement_id)
    if request.method == 'POST':
        behavior_statement.delete()
        return redirect('display_behavior_statements')
    return render(request, 'admin_template/delete_behavior_statement.html', {'behavior_statement': behavior_statement})

@require_GET
def get_master_data(request):
    master_id = request.GET.get('masterId')
    master = get_object_or_404(MT, id=master_id)
    data = {
        'id': master.id,
        'username': master.user.username,
        'first_name': master.user.first_name,
        'last_name': master.user.last_name,
    }
    return JsonResponse(data)

@require_POST
def update_master(request):
    master_id = request.POST.get('masterId')
    username = request.POST.get('userName')
    first_name = request.POST.get('firstName')
    last_name = request.POST.get('lastName')

    master = get_object_or_404(MT, id=master_id)
    before_master = f"{master.user.first_name} {master.user.last_name} {master.user.username}"
    master.user.username = username
    master.user.first_name = first_name
    master.user.last_name = last_name
    master.user.save()

    user = request.user
    action = f'{user} update master name "{master.user.username}, {before_master}" to {master.user.first_name} {master.user.last_name}"'
    details = f'{user} updated master name "{before_master}" to {master.user.first_name} {master.user.last_name} {master.user.username} in the system.'
    log_activity(user, action, details)

    logs = user, action, details    
    print(logs)

    return JsonResponse({'message': 'master updated successfully'})

@csrf_exempt
@login_required
def delete_master(request):
    if request.method == 'POST':
        master_id = request.POST.get('masterId')

        master = get_object_or_404(MT, id=master_id)

        try:
            user = request.user
            action = f'{user} delete master "{master.user.first_name} {master.user.last_name}"'
            details = f'{user} delete master {master.user.first_name} {master.user.last_name} in the system.'
            log_activity(user, action, details)

            logs = user, action, details    
            print(logs)
            user_id = master.user.id
            master.delete()

            user = get_object_or_404(get_user_model(), id=user_id)
            user.delete()

            response_data = {'message': 'master and associated user deleted successfully'}
            return JsonResponse(response_data)
        except Exception as e:
            response_data = {'message': f'Error deleting master and user: {str(e)}'}
            return JsonResponse(response_data, status=500)


@login_required
def home_admin(request):
    school_info = SchoolInformation.objects.first()
    if school_info is None:
        current_school_year = None
    else:
        current_school_year = school_info.school_year
        print(current_school_year)

    grades = Grade.objects.all()
    teachers = Teacher.objects.all()
    sections = Section.objects.all()
    total_teachers = Teacher.objects.count()
    total_students = Student.objects.filter(school_year=current_school_year).count()
    total_grades = Grade.objects.count()
    total_sections = Section.objects.count()
    total_subjects = Subject.objects.count()
   
    context = {
        'grades': grades,
        'sections': sections,
        'teachers': teachers,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_grades': total_grades,
        'total_sections': total_sections,
        'total_subjects': total_subjects,
        'school_year': current_school_year
    }
    return render(request, 'admin_template/home_admin.html', context)


def admin_base(request):
    announcements = Announcement.objects.all()
    return {'announcements': announcements}

@login_required
def add_teacher(request):
    return render(request, 'admin_template/add_teacher.html')

@login_required
def grade_and_section(request):
    grades = Grade.objects.all().order_by('name')
    sections = Section.objects.all()
    total_student = Section.objects.aggregate(total_students=models.Sum('total_students'))

    context = {
        'grades': grades,
        'sections': sections,
        'total_student': total_student['total_students'] if total_student else 0,
    }

    return render(request, 'admin_template/manage_grade_and_section.html', context)

@login_required
def teachers(request):
    grades = Grade.objects.all()
    teachers = Teacher.objects.all()
    sections = Section.objects.all()
    students = Student.objects.all()

    context = {
        'grades': grades,
        'sections': sections,
        'teachers': teachers,
        'students': students,
    }
    return render(request, 'admin_template/manage_teacher.html', context)

@login_required
def school_information_view(request):
    school_info = SchoolInformation.objects.all()
    context = {
        'school_info': school_info 
    }
    return render(request, 'admin_template/school_information_view.html', context)

@login_required
def add_school_view(request):
    if request.method == 'POST':
        form = SchoolInformationForm(request.POST)
        user = request.user
        action = f'{user} added new School Information'
        details = f'{user} added new School Information to the system.'
        log_activity(user, action, details)
        if form.is_valid():
            form.save()
        return redirect('school_information')
    else:
        return render(request, 'admin_template/add_school.html')
    
@login_required
def edit_school_view(request, school_id):
    school = get_object_or_404(SchoolInformation, id=school_id)

    if request.method == 'POST':
        user = request.user

        old_school_info = {
            'school_name': school.school_name,
            'region': school.region,
            'division': school.division,
            'school_id': school.school_id,
            'district': school.district,
            'school_year': school.school_year,
            'principal_name': school.principal_name
        }

        form = SchoolInformationForm(request.POST, instance=school)
        if form.is_valid():
            new_school_info = form.save()
            action = f'{user} changed the following fields in the School Information:\n' 
            details = f'{user} changed the following fields in the School Information:\n'
            for field, value in old_school_info.items():
                if getattr(new_school_info, field) != value:
                    action += f'{field}: {value} to {getattr(new_school_info, field)}\n'
                    details += f'{field}: {value} to {getattr(new_school_info, field)}\n'
            log_activity(user, action, details)
            return redirect('school_information')
    else:
        form = SchoolInformationForm(instance=school)

    return render(request, 'admin_template/edit_school.html', {'form': form, 'school': school})
    
@login_required
def delete_school_view(request, school_id):
    school = SchoolInformation.objects.get(id=school_id)
    user = request.user
    action = f'{user} deleted School Information'
    details = f'{user} deleted the School Information in the system.'
    log_activity(user, action, details)

    school.delete()
    return redirect('school_information')



@require_GET
def get_teacher_data(request):
    teacher_id = request.GET.get('teacherId')
    teacher = get_object_or_404(Teacher, id=teacher_id)
    data = {
        'id': teacher.id,
        'first_name': teacher.user.first_name,
        'last_name': teacher.user.last_name,
    }
    return JsonResponse(data)

def students(request):
    unique_combinations = Student.objects.values('grade', 'section').order_by('grade').distinct()
    data = []
    for combination in unique_combinations:
        grade = combination['grade']
        section = combination['section']
        total_students = Student.objects.filter(grade=grade, section=section).count()

        data.append({
            'grade': grade,
            'section': section,
            'total_students': total_students,
        })

    context = {
        'unique_grades_sections': data,
    }

    return render(request, 'admin_template/students.html', context)

def get_student_details(request):
    student_id = request.GET.get('studentId')
    student = get_object_or_404(Student, id=student_id)
    data = {
        'name': student.name,
    }
    return JsonResponse(data)

@require_POST
def update_student_details(request):
    student_id = request.POST.get('student_id')
    student_name = request.POST.get('student_name')
    student = get_object_or_404(Student, id=student_id)
    grade = student.grade
    section = student.section
    before_student = student.name
    student.name = student_name
    student.save()

    user = request.user
    action = f'{user} update student name "{before_student}" to "{student_name}"'
    details = f'{user} update student name "{before_student}" to "{student_name}" in the system.'
    log_activity(user, action, details)

    logs = user, action, details    
    print(logs)
    return JsonResponse({'message': 'Student details updated successfully'})

@require_POST
def delete_student(request):
    student_id = request.POST.get('student_id')
    student = get_object_or_404(Student, id=student_id)
    student_name = student.name
    user = request.user
    action = f'{user} delete student name "{student_name}"'
    details = f'{user} delete student name "{student_name}" in the system.'
    log_activity(user, action, details)

    logs = user, action, details    
    print(logs)

    student.delete()


    return JsonResponse({'message': 'Student deleted successfully'})

def student_lists(request):
    grade = request.GET.get('grade')
    section = request.GET.get('section')
    students = Student.objects.filter(grade=grade, section=section)

    context = {
        'grade': grade,
        'section': section,
        'students': students,

    }
    return render(request, 'admin_template/manage_students.html', context)

def student_lists_grade_section(request):
    grade = request.GET.get('grade')
    section = request.GET.get('section')
    students = Student.objects.filter(grade=grade, section=section)

    context = {
        'grade': grade,
        'section': section,
        'students': students,

    }
    return render(request, 'admin_template/manage_students.html', context)
def add_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        lrn = request.POST.get('lrn')
        sex = request.POST.get('sex')
        birthday = request.POST.get('birthday')
        grade = request.POST.get('grade')
        section = request.POST.get('section')
        default_values = Student.objects.filter(grade=grade, section=section).first()

        new_student = Student(
            grade=grade,
            section=section,
            name=name,
            lrn=lrn,
            sex=sex,
            birthday=birthday,
            teacher_id=default_values.teacher_id if default_values else None,
            school_id=default_values.school_id if default_values else None,
            school_name=default_values.school_name if default_values else None,
            school_year=default_values.school_year if default_values else None,
            division=default_values.division if default_values else None,
            district=default_values.district if default_values else None,
        )
        new_student.save()

        user = request.user
        action = f'{user} add student "{name}" to class "{grade} {section}"'
        details = f'{user} added student "{name}" to class "{grade} {section} in the system.'
        log_activity(user, action, details)

        logs = user, action, details    
        print(logs)

        redirect_url = reverse('student_lists', kwargs={'grade': grade, 'section': section})
    grade = request.GET.get('grade')
    section = request.GET.get('section')
    default_values = Student.objects.filter(grade=grade, section=section).first()

    context = {
        'default_values': default_values,
    }
    return render(request, 'admin_template/manage_students.html', context)


def subjects(request):
    subjects = Subject.objects.all()
    print(subjects)
    context = {
        'subjects': subjects,
    }
    return render(request, 'admin_template/manage_subjects.html', context)

def get_subject_data(request):
    subject_id = request.GET.get('subjectId')
    subject = get_object_or_404(Subject, id=subject_id)
    print(subject.assessment)
    data = {
        'id': subject.id,
        'name': subject.name,
        'assessment': subject.assessment,

    }

    return JsonResponse(data)


def add_subject(request):
    if request.method == 'POST':
        name = request.POST.get('name').upper()
        assessment = request.POST.get('assessment')

        if name and assessment:
            try:
                assessment_data = json.loads(assessment)
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error_message': 'Invalid JSON format for assessment'})

            subject = Subject.objects.create(
                name=name,
                assessment=assessment_data
            )
            return JsonResponse({'success': True, 'subject_id': subject.id})
        else:
            return JsonResponse({'success': False, 'error_message': 'Missing form data'})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


def subject_list(request):
    subjects = Subject.objects.all()
    print(subjects)
    return render(request, 'admin_template/subject_list.html', {'subjects': subjects})

def update_subject(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subjectId')  
        subject_name = request.POST.get('subjectName') 
        assessment_str = request.POST.get('assessment_update')
        assessment_str = assessment_str.replace('\\', '')
        try:
            assessment = json.loads(assessment_str)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid assessment data'})  

        subject = get_object_or_404(Subject, id=subject_id)
        subject.name = subject_name
        subject.assessment = assessment
        subject.save()

        user = request.user
        action = f'{user} updated "{subject_name}" subject information'
        details = f'{user} updated "{subject_name}" subject information in the system.'
        return JsonResponse({'success': True, 'message': 'Subject updated successfully'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
@login_required
def delete_subject(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subjectId')

        subject = get_object_or_404(Subject, id=subject_id)
        subject_name = subject.name
        user = request.user
        action = f'{user} delete "{subject_name}" subject'
        details = f'{user} delete "{subject_name}" subject in the system.'
        log_activity(user, action, details)

        logs = user, action, details    
        print(logs)
        subject.delete()
        return JsonResponse({'success': True, 'message': 'Subject deleted successfully'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def quarters(request):
    quarters = Quarters.objects.all()
    return render(request, 'admin_template/manage_quarters.html', {'quarters': quarters})

def add_quarter(request):
    if request.method == 'POST':
        quarters = request.POST.get('quarters')

        if quarters:
            quarter = Quarters.objects.create(
                quarters=quarters
            )
            return JsonResponse({'success': True, 'quarter_id': quarter.id})

    return JsonResponse({'success': False, 'error_message': 'Invalid form data'})
def get_quarters_data(request):
    quarter_id = request.GET.get('quarterId')
    quarter = get_object_or_404(Quarters, id=quarter_id)
    data = {
        'id': quarter.id,
        'quarters': quarter.quarters,
    }

    return JsonResponse(data)

@csrf_exempt
@login_required
def add_quarter(request):
    if request.method == 'POST':
        quarters = request.POST.get('quarters')

        if quarters:
            quarter = Quarters.objects.create(quarters=quarters)
            return JsonResponse({'success': True, 'quarter_id': quarter.id})

    return JsonResponse({'success': False, 'error_message': 'Invalid form data'})

def update_quarter(request):
    if request.method == 'POST':
        quarter_id = request.POST.get('quarterId')
        quarters = request.POST.get('quarters')

        quarter = get_object_or_404(Quarters, id=quarter_id)
        quarter.quarters = quarters
        quarter.save()

        return JsonResponse({'success': True, 'message': 'Quarter updated successfully'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
@login_required
def delete_quarter(request):
    if request.method == 'POST':
        quarter_id = request.POST.get('quarterId')

        quarter = get_object_or_404(Quarters, id=quarter_id)
        quarter.delete()

        return JsonResponse({'success': True, 'message': 'Quarter deleted successfully'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})
@require_POST
def update_teacher(request):
    teacher_id = request.POST.get('teacherId')
    first_name = request.POST.get('firstName')
    last_name = request.POST.get('lastName')

    teacher = get_object_or_404(Teacher, id=teacher_id)
    before_teacher = f"{teacher.user.first_name} {teacher.user.last_name}"
    teacher.user.first_name = first_name
    teacher.user.last_name = last_name
    teacher.user.save()

    user = request.user
    action = f'{user} update teacher name "{before_teacher}" to {teacher.user.first_name} {teacher.user.last_name}"'
    details = f'{user} updated teacher name "{before_teacher}" to {teacher.user.first_name} {teacher.user.last_name} in the system.'
    log_activity(user, action, details)

    logs = user, action, details    
    print(logs)

    return JsonResponse({'message': 'Teacher updated successfully'})
@csrf_exempt
@login_required
def delete_teacher(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacherId')
        teacher = get_object_or_404(Teacher, id=teacher_id)

        try:
            user = request.user
            action = f'{user} delete teacher "{teacher.user.first_name} {teacher.user.last_name}"'
            details = f'{user} delete teacher {teacher.user.first_name} {teacher.user.last_name} in the system.'
            log_activity(user, action, details)

            logs = user, action, details    
            print(logs)
            user_id = teacher.user.id
            teacher.delete()
            user = get_object_or_404(get_user_model(), id=user_id)
            user.delete()

            response_data = {'message': 'Teacher and associated user deleted successfully'}
            return JsonResponse(response_data)
        except Exception as e:
            response_data = {'message': f'Error deleting teacher and user: {str(e)}'}
            return JsonResponse(response_data, status=500)

def add_teacher_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('teachers')
    else:
        default = os.getenv("TEACHER")
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        middle_ini = request.POST.get('middle_ini', '')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password', default)
        user = request.user

        try:
                    
            action = f'{user} add teacher "{first_name} {last_name}"'
            details = f'{user} added teacher {first_name} {last_name} in the system.'
            log_activity(user, action, details)

            logs = user, action, details    
            print(logs)
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                middle_ini=middle_ini,
                user_type=2, 
            )

            return JsonResponse({'success': True, 'message': 'Teacher Added Successfully!'})
        except IntegrityError:
            messages.error(request, "Failed to Add Teacher!")
            return JsonResponse({'success': False, 'message': 'Failed to Add Teacher!'})
        
@require_GET
def get_sections(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        grade_id = request.GET.get('grade_id')
        sections = Section.objects.filter(grade_id=grade_id)
        section_list = [{'id': section.id, 'name': section.name} for section in sections]

        if section_list:
            return JsonResponse({'sections': section_list})
        else:
            return JsonResponse({'message': 'No sections available for the selected grade'})
    else:
        return JsonResponse({'message': 'Invalid request'})
    
def add_grade_section(request):
    grades = Grade.objects.all()
    sections = Section.objects.all()
    context = {
        'grades': grades,
        'sections': sections,
    }
    return render(request, 'admin_template/add_grade_section.html', context)


def search_students(request):
    if request.method == 'GET':
        search_query = request.GET.get('q', '')

        students = Student.objects.filter(
            Q(name__icontains=search_query) |
            Q(lrn__icontains=search_query) |
            Q(sex__icontains=search_query) |
            Q(birthday__icontains=search_query) |
            Q(teacher__id__icontains=search_query) |
            Q(grade__icontains=search_query) |
            Q(section__icontains=search_query)
        )

        context = {
            'students': students,
            'search_query': search_query,
        }

        return render(request, 'admin_template/home_admin.html', context)

def upload_documents_ocr(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['document']
            name = uploaded_file.name
            filename = 'processed_documents/' + name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '')
            file_extension = os.path.splitext(filename)[-1].lower()
            print(filename)
            
            
            if ProcessedDocument.objects.filter(document=filename).exists():
                messages.error(request, 'Document with the same name already exists.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            user = request.user
            action = f'{user} upload SF10 "{name}"'
            details = f'{user} upload SF10 "{name}" in the system.'
            log_activity(user, action, details)

            logs = user, action, details    
            print(logs)


            project_id = '404456621415'


            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"booming-post-418913-0158eec70d3f.json"

            client = documentai.DocumentProcessorServiceClient()

            processor_name = f"projects/{project_id}/locations/us/processors/8c21415e83206111"

            content = uploaded_file.read()

            file_extension = os.path.splitext(uploaded_file.name)[-1].lower()
            if file_extension in ['.pdf']:
                mime_type = "application/pdf"
            elif file_extension in ['.jpg', '.jpeg']:
                mime_type = "image/jpeg"
            else:
                return render(request, 'unsupported_file_type.html')

            processing_request = {
                "name": processor_name,
                "document": {"content": content, "mime_type": mime_type},
            }

            response = client.process_document(request=processing_request)

            document = response.document
            text = document.text

            data_by_type = {
                'Type': [],
                'Raw Value': [],
                'Normalized Value': [],
                'Confidence': [],
            }

            for entity in document.entities:
                data_by_type['Type'].append(entity.type_)
                data_by_type['Raw Value'].append(entity.mention_text)
                data_by_type['Normalized Value'].append(entity.normalized_value.text)
                data_by_type['Confidence'].append(f"{entity.confidence:.0%}")

                for prop in entity.properties:
                    data_by_type['Type'].append(prop.type_)
                    data_by_type['Raw Value'].append(prop.mention_text)
                    data_by_type['Normalized Value'].append(prop.normalized_value.text)
                    data_by_type['Confidence'].append(f"{prop.confidence:.0%}")

            print(data_by_type)
            processed_document = ProcessedDocument(document=uploaded_file, upload_date=timezone.now())
            processed_document.save()
            my_data = ExtractedData(processed_document=processed_document)
            key_mapping = {
                'Last_Name': 'last_name',
                'First_Name': 'first_name',
                'Middle_Name': 'middle_name',
                'SEX': 'sex',
                'Classified_as_Grade': 'classified_as_grade',
                'LRN': 'lrn',
                'Name_of_School': 'name_of_school',
                'School_Year': 'school_year',
                'General_Average': 'general_average',
                'Birthdate': 'birthdate',
            }
            last_values = {}
            for i in range(len(data_by_type['Type'])):
                data_type = data_by_type['Type'][i]
                raw_value = data_by_type['Raw Value'][i]

              
                last_values[data_type] = {'value': raw_value}

            for key, field_name in key_mapping.items():
                if key in last_values:
                    setattr(my_data, field_name, last_values[key]['value'])
            if 'Birthdate' in key_mapping:
                birthdate_index = data_by_type['Type'].index('Birthdate') if 'Birthdate' in data_by_type['Type'] else None
                if birthdate_index is not None:
                    birthdate_str = data_by_type['Raw Value'][birthdate_index]
                    try:
                        my_data.birthdate = parser.parse(birthdate_str).date()
                    except ValueError as e:
                        print(f"Error parsing birthdate: {e}")

            my_data.save()


            pdf_content_base64 = base64.b64encode(content).decode('utf-8')

        # return redirect('sf10_view')
        return render(request, 'admin_template/edit_extracted_data.html', {
                # 'extracted_data': extracted_data_for_review,
                'document_text': text,
                'uploaded_document_url': processed_document.document.url,
                # 'all_extracted_data': all_extracted_data,
                'processed_document': processed_document,
                'download_link': processed_document.document.url,
                'data_by_type': data_by_type,
                # 'extracted_text': extracted_text 
                'extracted_data': my_data,
                'pdf_content_base64': pdf_content_base64, 
            })
    else: 
        form = DocumentUploadForm()

    return render(request, 'admin_template/upload_documents.html', {'form': form})




def save_edited_data(request):  
    if request.method == 'POST':
        extracted_data = {
            'last_name': request.POST.get('Last_Name', ''),
            'first_name': request.POST.get('First_Name', ''),
            'middle_name': request.POST.get('Middle_Name', ''),
            'sex': request.POST.get('SEX', ''),
            'classified_as_grade': request.POST.get('Classified_as_Grade', ''),
            'lrn': request.POST.get('LRN', ''),
            'name_of_school': request.POST.get('Name_of_School', ''),
            'school_year': request.POST.get('School_Year', ''),
            'general_average': request.POST.get('General_Average', ''),
            'birthdate': request.POST.get('Birthdate', ''),
        }
        processed_document_id = request.POST.get('processed_document_id')
        print(f"Processed Document ID: {processed_document_id}")
        processed_document = ProcessedDocument.objects.get(pk=processed_document_id)

        try:
            extracted_data_instance = ExtractedData.objects.get(processed_document=processed_document)
        except ExtractedData.DoesNotExist:
            return HttpResponse("ExtractedData instance not found.")

        extracted_data_instance.last_name = extracted_data['last_name']
        extracted_data_instance.first_name = extracted_data['first_name']
        extracted_data_instance.middle_name = extracted_data['middle_name']
        extracted_data_instance.sex = extracted_data['sex']
        extracted_data_instance.classified_as_grade = extracted_data['classified_as_grade']
        extracted_data_instance.lrn = extracted_data['lrn']
        extracted_data_instance.name_of_school = extracted_data['name_of_school']
        extracted_data_instance.school_year = extracted_data['school_year']
        extracted_data_instance.general_average = extracted_data['general_average']

        birthdate_str = extracted_data['birthdate']

        try:
            formatted_birthdate = parser.parse(birthdate_str).date()
        except ValueError:
            return HttpResponse("Invalid birthdate format.")
        extracted_data_instance.birthdate = formatted_birthdate
        extracted_data_instance.save()

        return redirect('sf10_view')

    else:
        return HttpResponse("Invalid request method")

def sf10_views(request):
  
    search_query = request.GET.get('search', '')
    if search_query:
        search_fields = ['last_name', 'first_name', 'middle_name', 'lrn', 'name_of_school', 'sex', 'birthdate', 'school_year', 'classified_as_grade', 'general_average', 'processed_document__teacher__user__first_name', 'processed_document__teacher__user__last_name', 'processed_document__upload_date']
        query = Q()
        for field in search_fields:
            query |= Q(**{f'{field}__icontains': search_query})
        all_extracted_data = ExtractedData.objects.filter(query)
    else:
        all_extracted_data = ExtractedData.objects.all()
    context = {
        'all_extracted_data': all_extracted_data,
        'search_query': search_query,
    }
    return render(request, 'admin_template/sf10.html', context)

def announcement(request):
    announcements = Announcement.objects.all()
    return render(request, 'admin_template/announcement.html', {'announcements': announcements})

def create_announcement(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        try:
            Announcement.objects.create(title=title, content=content)
            messages.success(request, 'Announcement created successfully')
            return render(request, 'admin_template/announcement.html')
        except Exception as e:
            messages.error(request, f'Failed to create Announcement: {e}')

    return render(request, 'admin_template/announcement.html')

def delete_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    try:
        announcement.delete()
        return JsonResponse({'success': True, 'message': 'Announcement deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Failed to delete announcement: {e}'})


def user_list(request):
    teachers = CustomUser.objects.filter(user_type=2)
    return render(request, 'teacher_list.html', {'teachers': teachers})

def user_activities(request):
    user_id = request.GET.get('id')
    if user_id:
        activities = ActivityLog.objects.filter(user_id=user_id).order_by('-timestamp')
        
        # Pagination
        paginator = Paginator(activities, 7) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'admin_template/user_activities.html', {'page_obj': page_obj, 'user_id': user_id})
    else:
        return render(request, 'admin_template/user_activities.html', {'error_message': 'User ID is required'})

    
def download_activities(request):
    user_id = request.GET.get('id')
    if user_id:
        activities = ActivityLog.objects.filter(user_id=user_id).order_by('-timestamp')
        filename = f"user_{user_id}_activities.xlsx"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        workbook = Workbook()
        worksheet = workbook.active
        headers = ['Timestamp', 'Action', 'Details']
        worksheet.append(headers)
        for activity in activities:
            worksheet.append([activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'), activity.action, activity.details])
        workbook.save(filepath)
        with open(filepath, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return HttpResponse('User ID is required', status=400)

   
def sf10_edit_view(request, id):
    extracted_data = get_object_or_404(ExtractedData, id=id)
    processed_document = extracted_data.processed_document
    pdf_content = processed_document.document.read()
    pdf_content_base64 = base64.b64encode(pdf_content).decode('utf-8')
    return render(request, 'admin_template/edit_sf10.html', {'extracted_data': extracted_data, 'pdf_content_base64': pdf_content_base64})

def sf10_edit(request, id):

    extracted_data = get_object_or_404(ExtractedData, id=id)

    if request.method == 'POST':
        extracted_data.last_name = request.POST.get('Last_Name', '')
        extracted_data.first_name = request.POST.get('First_Name', '')
        extracted_data.middle_name = request.POST.get('Middle_Name', '')
        extracted_data.sex = request.POST.get('SEX', '')
        extracted_data.classified_as_grade = request.POST.get('Classified_as_Grade', '')
        extracted_data.lrn = request.POST.get('LRN', '')
        extracted_data.name_of_school = request.POST.get('Name_of_School', '')
        extracted_data.school_year = request.POST.get('School_Year', '')
        extracted_data.general_average = request.POST.get('General_Average', '')

        sf10_name = f"{extracted_data.first_name} {extracted_data.last_name}"
        user = request.user
        action = f'{user} updates information of the SF10 of "{sf10_name}"'
        details = f'{user} updates information of the SF10 of "{sf10_name} in the system.'
        log_activity(user, action, details)

        logs = user, action, details    
        print(logs)
        birthdate_str = request.POST.get('Birthdate', '')
        try:
            birthdate_obj = datetime.strptime(birthdate_str, "%b. %d, %Y")
            extracted_data.birthdate = birthdate_obj.strftime("%Y-%m-%d")
        except ValueError:
            pass  
        extracted_data.save()
        return HttpResponseRedirect(reverse('sf10_view') + '?success=true')
    return render(request, 'admin_template/edit_sf10.html', {'extracted_data': extracted_data})


def sf10_delete(request):
    if request.method == 'POST':

        delete_id = request.POST.get('delete_id')
        extracted_data = get_object_or_404(ExtractedData, id=delete_id)

        sf10_name = f"{extracted_data.first_name} {extracted_data.last_name}"
        user = request.user
        action = f'{user} delete "{sf10_name}" SF10'
        details = f'{user} delete "{sf10_name}" SF10 in the system.'
        log_activity(user, action, details)

        logs = user, action, details    
        print(logs)

        extracted_data.delete()
        return redirect('sf10_view')
    else:
        return redirect('sf10_view')

def download_processed_document(request, id):
    extracted_data = get_object_or_404(ExtractedData, id=id)        
    processed_document = extracted_data.processed_document
    file_path = processed_document.document.path
    print(processed_document)
    print(file_path)
    sf10_name = f"{extracted_data.first_name} {extracted_data.last_name}"
    user = request.user
    action = f'{user} download "{sf10_name}" SF10'
    details = f'{user} delete "{sf10_name}" SF10 in the system.'
    log_activity(user, action, details)

    logs = user, action, details    
    print(logs)

    response = FileResponse(processed_document.document, as_attachment=True)
    filename_without_path = processed_document.document.name.split('/')[-1]

    response['Content-Disposition'] = f'attachment; filename="{filename_without_path}"'
    return response


def batch_process_documents(request):

    if request.method == 'POST':
        form = DocumentBatchUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_files = request.FILES.getlist('documents')
            for uploaded_file in uploaded_files:
                name = uploaded_file.name
                filename = 'processed_documents/' + name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '')

                if ProcessedDocument.objects.filter(document=filename).exists():
                    messages.error(request, f'Document "{name}" already exists.')
                    continue
                user = request.user
                action = f'{user} upload SF10 "{name}"'
                details = f'{user} upload SF10 "{name}" in the system.'
                log_activity(user, action, details)
                logs = user, action, details    
                print(logs)
                project_id = '404456621415'
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"booming-post-418913-0158eec70d3f.json"
                client = documentai.DocumentProcessorServiceClient()
                processor_name = f"projects/{project_id}/locations/us/processors/8c21415e83206111"
                content = uploaded_file.read()
                file_extension = os.path.splitext(uploaded_file.name)[-1].lower()
                if file_extension in ['.pdf']:
                    mime_type = "application/pdf"
                elif file_extension in ['.jpg', '.jpeg']:
                    mime_type = "image/jpeg"
                else:
                    messages.error(request, f'Unsupported file type for document "{name}".')
                    continue
                processing_request = {
                    "name": processor_name,
                    "document": {"content": content, "mime_type": mime_type},
                }
                try:
                    response = client.process_document(request=processing_request)
                    document = response.document
                    text = document.text
                    data_by_type = {
                        'Type': [],
                        'Raw Value': [],
                        'Normalized Value': [],
                        'Confidence': [],
                    }
                    for entity in document.entities:
                        data_by_type['Type'].append(entity.type_)
                        data_by_type['Raw Value'].append(entity.mention_text)
                        data_by_type['Normalized Value'].append(entity.normalized_value.text)
                        data_by_type['Confidence'].append(f"{entity.confidence:.0%}")
                        for prop in entity.properties:
                            data_by_type['Type'].append(prop.type_)
                            data_by_type['Raw Value'].append(prop.mention_text)
                            data_by_type['Normalized Value'].append(prop.normalized_value.text)
                            data_by_type['Confidence'].append(f"{prop.confidence:.0%}")

                    print(data_by_type)

                    processed_document = ProcessedDocument(document=uploaded_file, upload_date=timezone.now())
                    processed_document.save()

                    my_data = ExtractedData(processed_document=processed_document)
                    key_mapping = {
                        'Last_Name': 'last_name',
                        'First_Name': 'first_name',
                        'Middle_Name': 'middle_name',
                        'SEX': 'sex',
                        'Classified_as_Grade': 'classified_as_grade',
                        'LRN': 'lrn',
                        'Name_of_School': 'name_of_school',
                        'School_Year': 'school_year',
                        'General_Average': 'general_average',
                        'Birthdate': 'birthdate',
                    }

                    last_values = {}

                    for i in range(len(data_by_type['Type'])):
                        data_type = data_by_type['Type'][i]
                        raw_value = data_by_type['Raw Value'][i]
                        last_values[data_type] = {'value': raw_value}
                    for key, field_name in key_mapping.items():
                        if key in last_values:
                            setattr(my_data, field_name, last_values[key]['value'])
                    if 'Birthdate' in key_mapping:
                        birthdate_index = data_by_type['Type'].index('Birthdate') if 'Birthdate' in data_by_type['Type'] else None
                        if birthdate_index is not None:
                            birthdate_str = data_by_type['Raw Value'][birthdate_index]
                            try:
                                my_data.birthdate = parser.parse(birthdate_str).date()
                            except ValueError as e:
                                print(f"Error parsing birthdate: {e}")

                    my_data.save()


                except Exception as e:
                    messages.error(request, f'Error processing document "{name}": {str(e)}')

            messages.success(request, 'Documents processed successfully.')
            return redirect('sf10_view')
    else:
        form = DocumentBatchUploadForm()

    return render(request, 'admin_template/batch_process_documents.html', {'form': form})

def process_document_form_sample(
    project_id: str,
    location: str,
    processor_id: str,
    processor_version: str,
    content: bytes,
    mime_type: str,
) -> documentai.Document:
    client_options = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=client_options)

    name = client.processor_version_path(project_id, location, processor_id, processor_version)

    request = documentai.ProcessRequest(
        name=name,
        raw_document=documentai.RawDocument(content=content, mime_type=mime_type),
    )

    result = client.process_document(request=request)

    return result.document


def detect_and_convert_tables(request):
    if request.method == 'POST' and 'pdf_file' in request.FILES:
        pdf_file = request.FILES['pdf_file']
        content = pdf_file.read()

       
        project_id = "1083879771832"
        location = "us"  
        processor_id = "827ebb48ef18ecd"  
        processor_version = "pretrained-form-parser-v2.0-2022-11-10"  
        try:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"ces-ocr-5a2441a9fd54.json"
            document = process_document_form_sample(project_id, location, processor_id, processor_version, content, "application/pdf")
            table_data = []

            for page in document.pages:
                for table in page.tables:
                    for row in table.header_rows:
                        row_content = [layout_to_text(cell.layout, document.text) for cell in row.cells]
                        row_hps = "HIGHEST POSSIBLE SCORE"
                        table_data.append(row_content)

                    for row in table.body_rows:
                        row_content = [layout_to_text(cell.layout, document.text) for cell in row.cells]
                        table_data.append(row_content)

            print(table_data)

            form_fields_data = []

            grade_section = "GRADE & SECTION:"
            teacher = "TEACHER:"
            grade_section_present = False
            teacher_present = False

            for page in document.pages:
                for field in page.form_fields:
                    name = layout_to_text(field.field_name, document.text).strip()
                    value = layout_to_text(field.field_value, document.text).strip()

                    form_field_data = {'name': name, 'value': value}

                    form_fields_data.append(form_field_data)

                    # Check if the name matches the grade_section
                    if name == grade_section:
                        grade_section_present = True
                    elif name == teacher:
                            teacher_present = True

                if grade_section_present and teacher_present:
                    print("Both GRADE & SECTION and TEACHER fields are present together")
                else:
                    print("Either GRADE & SECTION or TEACHER field is missing")


            json_data = {'table_data': table_data, 'form_fields_data': form_fields_data}
            json_file_path = 'document_data.json'
            with open(json_file_path, 'w') as json_file:
                json.dump(json_data, json_file)

            print(f'Table data saved to {json_file_path}')
 
            return render(request, 'admin_template/table_data.html', {'table_data': table_data, 'form_fields_data': form_fields_data })

        except Exception as e:
            return HttpResponse(f'Error processing PDF: {str(e)}')

    return render(request, 'admin_template/detect_and_convert_tables.html')

def layout_to_text(layout, document_text):
    """
    Extracts text content from the layout of a Document AI element.
    """
    text_content = ""
    for text_segment in layout.text_anchor.text_segments:
        start_index = text_segment.start_index
        end_index = text_segment.end_index
        text_content += document_text[start_index:end_index]
    return text_content


