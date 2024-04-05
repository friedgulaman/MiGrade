from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from CuyabSRMS.models import MT, Grade, SuperAdmin, Admin, CustomUser, ActivityLog
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


from django.http import HttpResponse
from subprocess import run, PIPE

def backup_database(request):
    # Execute the dbbackup command
    # result = run(['python', 'manage.py', 'dbbackup', '--encrypt'], stdout=PIPE, stderr=PIPE)
    result = run(['python', 'manage.py', 'dbbackup'], stdout=PIPE, stderr=PIPE)
    
    if result.returncode == 0:
        # Backup successful
        return HttpResponse("Backup successful")
    else:
        # Backup failed
        return HttpResponse("Backup failed: " + result.stderr.decode('utf-8'), status=500)
    
@login_required
def home_superadmin(request):
    admins = Admin.objects.all()
    masters = MT.objects.all()

    context = {
        'admins': admins,
        'masters': masters,
    }
    return render(request, 'superadmin_template/home_superadmin.html', context)



@login_required
def super_manage_master_teacher(request):
        return render(request, 'superadmin_template/manage_master_teacher.html')

@login_required
def manage_teacher(request):
        return render(request, 'superadmin_template/manage_teacher.html')

@login_required
def manage_admin(request):
        
        return render(request, 'superadmin_template/home_superadmin.html')


def add_admin(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('home_superadmin')
    else:
        default = os.getenv("ADMIN")
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        middle_ini = request.POST.get('middle_ini')
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password', default)
        user = request.user

        try:
            # Create a CustomUser
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                middle_ini=middle_ini,
                user_type=3,  # This represents an admin user
            )

            logger.debug('Admin added successfully!')
            return JsonResponse({'success': True, 'message': 'Admin Added Successfully!'})
        except IntegrityError as e:
            logger.exception('Failed to add Admin: %s', e)
            messages.error(request, "Failed to Add Admin!")

            # Return a JSON response for error
            return JsonResponse({'success': False, 'message': 'Failed to Add Admin!'})


@require_GET
def get_admin_data(request):
    admin_id = request.GET.get('adminId')
    admin = get_object_or_404(Admin, id=admin_id)
    data = {
        'id': admin.id,
        'username': admin.user.username,
        'first_name': admin.user.first_name,
        'last_name': admin.user.last_name,
    }
    return JsonResponse(data)

@require_POST
def update_admin(request):
    admin_id = request.POST.get('adminId')
    username = request.POST.get('userName')
    first_name = request.POST.get('firstName')
    last_name = request.POST.get('lastName')

    admin = get_object_or_404(Admin, id=admin_id)
    before_admin = f"{admin.user.first_name} {admin.user.last_name} {admin.user.username}"
    admin.user.username = username
    admin.user.first_name = first_name
    admin.user.last_name = last_name
    admin.user.save()

    user = request.user
    action = f'{user} update admin name "{admin.user.username}, {before_admin}" to {admin.user.first_name} {admin.user.last_name}"'
    details = f'{user} updated admin name "{before_admin}" to {admin.user.first_name} {admin.user.last_name} {admin.user.username} in the system.'
    log_activity(user, action, details)

    logs = user, action, details    
    print(logs)

    return JsonResponse({'message': 'admin updated successfully'})

@csrf_exempt
@login_required
def delete_admin(request):
    if request.method == 'POST':
        admin_id = request.POST.get('adminId')

        # Check if the admin exists
        admin = get_object_or_404(Admin, id=admin_id)

        try:
            user = request.user
            action = f'{user} delete admin "{admin.user.first_name} {admin.user.last_name}"'
            details = f'{user} delete admin {admin.user.first_name} {admin.user.last_name} in the system.'
            log_activity(user, action, details)

            logs = user, action, details    
            print(logs)
            # Perform the admin deletion
            user_id = admin.user.id  # Get the associated user ID
            admin.delete()


            # Delete the associated CustomUser
            user = get_object_or_404(get_user_model(), id=user_id)
            user.delete()

            response_data = {'message': 'admin and associated user deleted successfully'}
            return JsonResponse(response_data)
        except Exception as e:
            response_data = {'message': f'Error deleting admin and user: {str(e)}'}
            return JsonResponse(response_data, status=500)



# superadmin
@login_required
def manage_master_teacher(request):
        masters = MT.objects.all()
        return render(request, 'superadmin_template/manage_master.html', {'masters': masters})

@login_required
def assign_master(request):
    all_grades = Grade.objects.all()
    assigned_grades = set()

    # Collect all assigned grades from MT instances
    for mt in MT.objects.all():
        assigned_grades.update(mt.assigned_grades)

    # Filter grades based on whether they are assigned or not
    unassigned_grades = [grade for grade in all_grades if grade.name not in assigned_grades]

    context = {
        'grades': unassigned_grades,
        'masters': MT.objects.all(),
    }
    return render(request, 'superadmin_template/assign_master.html', context)


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
            # Create a CustomUser
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                middle_ini=middle_ini,
                user_type=4,  # This represents an admin user
            )

            logger.debug('Admin added successfully!')
            return JsonResponse({'success': True, 'message': 'Admin Added Successfully!'})
        except IntegrityError as e:
            logger.exception('Failed to add Admin: %s', e)
            messages.error(request, "Failed to Add Admin!")

            # Return a JSON response for error
            return JsonResponse({'success': False, 'message': 'Failed to Add Admin!'})


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

        # Check if the master exists
        master = get_object_or_404(MT, id=master_id)

        try:
            user = request.user
            action = f'{user} delete master "{master.user.first_name} {master.user.last_name}"'
            details = f'{user} delete master {master.user.first_name} {master.user.last_name} in the system.'
            log_activity(user, action, details)

            logs = user, action, details    
            print(logs)
            # Perform the master deletion
            user_id = master.user.id  # Get the associated user ID
            master.delete()


            # Delete the associated CustomUser
            user = get_object_or_404(get_user_model(), id=user_id)
            user.delete()

            response_data = {'message': 'master and associated user deleted successfully'}
            return JsonResponse(response_data)
        except Exception as e:
            response_data = {'message': f'Error deleting master and user: {str(e)}'}
            return JsonResponse(response_data, status=500)
