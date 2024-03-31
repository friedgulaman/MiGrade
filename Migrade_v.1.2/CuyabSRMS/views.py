from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .EmailBackEnd import EmailBackEnd  # Update the import path
from .models import MT, ActivityLog, Admin, Announcement, SchoolInformation, SuperAdmin, Teacher
from .utils import log_activity
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
import os
from dotenv import load_dotenv
load_dotenv()



def custom_404(request, exception=None):
    return render(request, 'custom_404.html', status=404) 
    
def home_superadmin(request):
    return render(request, 'superadmin_template/home_superadmin.html') 

def activity(request):
    if request.user.is_authenticated:
        user = request.user
        activity_logs = ActivityLog.objects.filter(user=user).order_by('-timestamp')
        
        # Pagination
        paginator = Paginator(activity_logs, 7)  # Show 7 activity logs per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'teacher_template/teachers_activity.html', {'page_obj': page_obj})
    else:
        return HttpResponse("Please log in to view your activity logs.")



def ShowLoginPage(request):
    public = os.getenv("RECAPTCHA_PUBLIC_KEY")  # Get the public key
    if request.user.is_authenticated:
        # User is already logged in, so redirect them to the appropriate page based on user type
        if request.user.user_type == 1:  # SuperAdmin user type
            return redirect('home_superadmin')
        elif request.user.user_type == 2:  # Teacher user type
            return redirect('home_teacher')
        elif request.user.user_type == 3:  # Admin user type
            return redirect('home_admin')
        elif request.user.user_type == 4:  # MT user type
            return redirect('home_mt')
        else:
            # Handle other user types or redirect to a generic home page
            pass
    # Pass the public key to the template context
    context = {
        'public_key': public,
    }
    
    return render(request, 'login_page.html', context)

def doLogin(request):
    if request.method == "POST":
        captcha_response = request.POST.get("g-recaptcha-response")
        captcha = os.getenv("CAPTCHA")

        if not captcha_response:
            messages.error(request, "Please complete the reCAPTCHA.")
            return redirect('ShowLoginPage')
        
        data = {
            'secret': captcha,
            'response': captcha_response
        }
        
        response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
        result = response.json()
        
        if result['success']:
            user = EmailBackEnd().authenticate(
                request, username=request.POST.get('email'), password=request.POST.get('password')
            )
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Log the user login activity
                action = f'{user} logged in'
                details = f'{user} logged in to the system.'
                log_activity(user, action, details)
                
                if user.user_type == 1:
                    return redirect('home_superadmin')
                elif user.user_type == 2:
                    return redirect('home_teacher') 
                elif user.user_type == 3:
                    return redirect('home_admin')
                elif user.user_type == 4:
                    return redirect('home_mt')
                else:
                    # Handle other user types or redirect to a generic home page
                    pass
            else:
                messages.error(request, "Invalid Login Credentials!")
        else:
            messages.error(request, "Invalid reCAPTCHA. Please try again.")
    return redirect('ShowLoginPage')

def get_user_details(request):
    if request.user.is_authenticated:
        return HttpResponse("User: " + request.user.email + " User Type: " + request.user.user_type)
    else:
        return HttpResponse("Please Login First")
    
def logout_user(request):
    request.session.flush()  # or request.session.clear()
    messages.success(request, "Logout successfully!")
    return redirect('/')

@login_required
def profile_page(request):
    user = request.user  # Get the logged-in user
    user_type = user.user_type  # Get the user type
    context = {}

    if user_type == 2:  # Assuming '2' represents a teacher user type
        teacher = get_object_or_404(Teacher, user=user)  # Get the teacher object associated with the user
        context['teacher'] = teacher

    return render(request, 'teacher_template/teacher_profile.html', context)



def password_reset_sent(request):
     return render(request, 'password_reset_sent.html')



def update_profile_photo(request):
    if request.method == "POST":
        profile_photo = request.FILES.get("profile_photo")
        if profile_photo:
            # Save the new profile photo
            request.user.profile_image = profile_photo
            request.user.save()
            
            # Log the activity of updating the profile photo
            user = request.user
            action = 'Profile photo updated'
            details = 'User updated their profile photo.'
            log_activity(user, action, details)
            
            # Redirect to the user's profile page or a success page
            return redirect('profile_page')

    return render(request, 'profile_page')

def update_teacher_profile(request):
    if request.method == "POST":
        user = request.user
        # Update the user's profile information with the submitted data
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.middle_ini = request.POST.get('middle_ini')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()

        # Log the activity of updating the teacher's profile
        action = 'Teacher profile updated'
        details = 'Teacher updated their profile information.'
        log_activity(user, action, details)

        messages.success(request, 'Profile updated successfully.')  # Display a success message
        return redirect('profile_page')  # Redirect to the updated profile page

    return render(request, 'profile_page')


@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = request.user

        if user.check_password(old_password):
            if new_password == confirm_password:
                if not user.check_password(new_password):
                    # Ensure the new password is different from the old one
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # To maintain the user's session

                    # Log the activity of changing the password
                    action = 'Password changed'
                    details = 'User changed their password.'
                    log_activity(user, action, details)

                    # Add a success message
                    messages.success(request, 'Password changed successfully.')
                    return redirect('profile_page')  # Replace 'profile' with the name of the view you want to redirect to

                else:
                    # Add an error message
                    messages.error(request, 'New password must be different from the old password.')

            else:
                # Add an error message
                messages.error(request, 'New password and confirm password do not match.')

        else:
            # Add an error message
            messages.error(request, 'Invalid old password')

    return redirect('profile_page')  # Replace 'profile' with the name of the view you want to redirect to



@login_required
def admin_profile_page(request):
    user = request.user  # Get the logged-in user
    user_type = user.user_type  # Get the user type
    context = {}

    if user_type == 3:  # Assuming '2' represents a admin user type
        admin = get_object_or_404(Admin, user=user)  # Get the admin object associated with the user
        context['admin'] = admin

    return render(request, 'admin_template/admin_profile.html', context)
    

def admin_update_profile_photo(request):
    if request.method == "POST":
        profile_photo = request.FILES.get("profile_photo")
        if profile_photo:
            # Save the new profile photo
            request.user.profile_image = profile_photo
            request.user.save()
            
            # Log the activity of updating the profile photo
            user = request.user
            action = 'Profile photo updated'
            details = 'User updated their profile photo.'
            log_activity(user, action, details)
            
            # Redirect to the user's profile page or a success page
            return redirect('admin_profile_page')

    return render(request, 'admin_profile_page')

def admin_update_profile(request):
    if request.method == "POST":
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()

        # Log the activity of updating the teacher's profile
        action = 'Admin profile updated'
        details = 'Admin updated their profile information.'
        log_activity(user, action, details)

        messages.success(request, 'Profile updated successfully.')  # Display a success message
        return redirect('admin_profile_page')  # Redirect to the updated profile page

    return render(request, 'admin_profile_page')


@login_required
def admin_change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = request.user

        if user.check_password(old_password):
            if new_password == confirm_password:
                if not user.check_password(new_password):
                    # Ensure the new password is different from the old one
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # To maintain the user's session

                    # Log the activity of changing the password
                    action = 'Password changed'
                    details = 'User changed their password.'
                    log_activity(user, action, details)

                    # Add a success message
                    messages.success(request, 'Password changed successfully.')
                    return redirect('admin_profile_page')  # Replace 'profile' with the name of the view you want to redirect to

                else:
                    # Add an error message
                    messages.error(request, 'New password must be different from the old password.')

            else:
                # Add an error message
                messages.error(request, 'New password and confirm password do not match.')

        else:
            # Add an error message
            messages.error(request, 'Invalid old password')

    return redirect('admin_profile_page')  # Replace 'profile' with the name of the view you want to redirect to


@login_required
def mt_profile_page(request):
    user = request.user  # Get the logged-in user
    user_type = user.user_type  # Get the user type
    context = {}

    if user_type == 4:  # Assuming '2' represents a mt user type
        mt = get_object_or_404(MT, user=user)  # Get the mt object associated with the user
        context['mt'] = mt

    return render(request, 'master_template/master_profile.html', context)
    

def mt_update_profile_photo(request):
    if request.method == "POST":
        profile_photo = request.FILES.get("profile_photo")
        if profile_photo:
            # Save the new profile photo
            request.user.profile_image = profile_photo
            request.user.save()
            
            # Log the activity of updating the profile photo
            user = request.user
            action = 'Profile photo updated'
            details = 'User updated their profile photo.'
            log_activity(user, action, details)
            
            # Redirect to the user's profile page or a success page
            return redirect('mt_profile_page')

    return render(request, 'mt_profile_page')

def mt_update_profile(request):
    if request.method == "POST":
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()

        # Log the activity of updating the teacher's profile
        action = 'mt profile updated'
        details = 'mt updated their profile information.'
        log_activity(user, action, details)

        messages.success(request, 'Profile updated successfully.')  # Display a success message
        return redirect('mt_profile_page')  # Redirect to the updated profile page

    return render(request, 'mt_profile_page')


@login_required
def mt_change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = request.user

        if user.check_password(old_password):
            if new_password == confirm_password:
                if not user.check_password(new_password):
                    # Ensure the new password is different from the old one
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # To maintain the user's session

                    # Log the activity of changing the password
                    action = 'Password changed'
                    details = 'User changed their password.'
                    log_activity(user, action, details)

                    # Add a success message
                    messages.success(request, 'Password changed successfully.')
                    return redirect('mt_profile_page')  # Replace 'profile' with the name of the view you want to redirect to

                else:
                    # Add an error message
                    messages.error(request, 'New password must be different from the old password.')

            else:
                # Add an error message
                messages.error(request, 'New password and confirm password do not match.')

        else:
            # Add an error message
            messages.error(request, 'Invalid old password')

    return redirect('mt_profile_page')  # Replace 'profile' with the name of the view you want to redirect to


@login_required
def super_profile_page(request):
    user = request.user  # Get the logged-in user
    user_type = user.user_type  # Get the user type
    context = {}

    if user_type == 1:  # Assuming '2' represents a super user type
        super = get_object_or_404(SuperAdmin, user=user)  # Get the super object associated with the user
        context['super'] = super

    return render(request, 'superadmin_template/super_profile.html', context)
    

def super_update_profile_photo(request):
    if request.method == "POST":
        profile_photo = request.FILES.get("profile_photo")
        if profile_photo:
            # Save the new profile photo
            request.user.profile_image = profile_photo
            request.user.save()
            
            # Log the activity of updating the profile photo
            user = request.user
            action = 'Profile photo updated'
            details = 'User updated their profile photo.'
            log_activity(user, action, details)
            
            # Redirect to the user's profile page or a success page
            return redirect('super_profile_page')

    return render(request, 'super_profile_page')

def super_update_profile(request):
    if request.method == "POST":
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()

        # Log the activity of updating the teacher's profile
        action = 'super profile updated'
        details = 'super updated their profile information.'
        log_activity(user, action, details)

        messages.success(request, 'Profile updated successfully.')  # Display a success message
        return redirect('super_profile_page')  # Redirect to the updated profile page

    return render(request, 'super_profile_page')


@login_required
def super_change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = request.user

        if user.check_password(old_password):
            if new_password == confirm_password:
                if not user.check_password(new_password):
                    # Ensure the new password is different from the old one
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # To maintain the user's session

                    # Log the activity of changing the password
                    action = 'Password changed'
                    details = 'User changed their password.'
                    log_activity(user, action, details)

                    # Add a success message
                    messages.success(request, 'Password changed successfully.')
                    return redirect('super_profile_page')  # Replace 'profile' with the name of the view you want to redirect to

                else:
                    # Add an error message
                    messages.error(request, 'New password must be different from the old password.')

            else:
                # Add an error message
                messages.error(request, 'New password and confirm password do not match.')

        else:
            # Add an error message
            messages.error(request, 'Invalid old password')

    return redirect('super_profile_page')  # Replace 'profile' with the name of the view you want to redirect to
