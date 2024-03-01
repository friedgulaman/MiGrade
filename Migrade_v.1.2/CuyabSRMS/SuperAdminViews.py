from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from CuyabSRMS.models import SuperAdmin, Admin, CustomUser, ActivityLog
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
def home_superadmin(request):
        return render(request, 'superadmin_template/home_superadmin.html')



@login_required
def super_manage_master_teacher(request):
        return render(request, 'superadmin_template/manage_master_teacher.html')

@login_required
def manage_teacher(request):
        return render(request, 'superadmin_template/manage_teacher.html')

@login_required
def manage_admin(request):
        admins = Admin.objects.all()
        return render(request, 'superadmin_template/manage_admin.html', {'admins': admins})


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
