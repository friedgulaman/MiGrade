from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .EmailBackEnd import EmailBackEnd  # Update the import path
from .models import ActivityLog, Admin, Teacher  # Import the ActivityLog and Teacher models
from .utils import log_activity
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


def custom_404(request, exception=None):
    return render(request, 'custom_404.html', status=404) 
    
def teachers_activity(request):
    if request.user.is_authenticated:
        user = request.user
        activity_logs = ActivityLog.objects.filter(user=user).order_by('-timestamp')
        return render(request, 'teacher_template/teachers_activity.html', {'activity_logs': activity_logs})
    else:
        return HttpResponse("Please log in to view your activity logs.")

@login_required
def admin_activity(request):
    try:
        admin = Admin.objects.get(username=request.user)
        custom_user = admin.username  # Assuming 'username' is the ForeignKey to CustomUser in Admin model
        activity_logs = ActivityLog.objects.filter(user=custom_user).order_by('-timestamp')
        return render(request, 'admin_template/admin_activity.html', {'activity_logs': activity_logs})
    except Admin.DoesNotExist:
        return HttpResponse("User does not have associated admin information.")
    except ActivityLog.DoesNotExist:
        return render(request, 'admin_template/admin_activity.html', {'activity_logs': []})
    
def ShowLoginPage(request):
    if request.user.is_authenticated:
        # User is already logged in, so redirect them to the home page or the appropriate page
        if request.user.user_type == 2:  # Assuming '2' represents a teacher user type
            return redirect('home_teacher')
        else:
            return redirect('home_admin')
    else:
        return render(request, 'login_page.html')

def doLogin(request):
    if request.method == "POST":
        captcha_response = request.POST.get("g-recaptcha-response")
        
        if not captcha_response:
            messages.error(request, "Please complete the reCAPTCHA.")
            return redirect('ShowLoginPage')
        
        data = {
            'secret': '6LdtT_UoAAAAABm6NBYEVktmHP2vIGajVg2_kzJW',
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
                user = request.user
                action = 'User logged in'
                details = 'User logged in to the system.'
                log_activity(user, action, details)
                
                if user.user_type == 2:
                    return redirect('home_teacher')
                else:
                    return redirect('home_admin')
            else:
                messages.error(request, "Invalid Login Credentials!")
                return redirect('ShowLoginPage')
        else:
            messages.error(request, "Invalid reCAPTCHA. Please try again.")
            return redirect('ShowLoginPage')
    else:
        return HttpResponse("<h2>Method Not Allowed</h2>")

def get_user_details(request):
    if request.user.is_authenticated:
        return HttpResponse("User: " + request.user.email + " User Type: " + request.user.user_type)
    else:
        return HttpResponse("Please Login First")

def logout_user(request):
    logout(request)
    messages.success(request, "Logout successfully!")
    return HttpResponseRedirect('/')

@login_required
def profile_page(request):
    user = request.user  # Get the logged-in user
    user_type = user.user_type  # Get the user type
    if user_type == 2:  # Assuming '2' represents a teacher user type
        teacher = Teacher.objects.get(user=user)  # Get the teacher object associated with the user
        context = {
            'teacher': teacher,
        }
        return render(request, 'teacher_template/teacher_profile.html')



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
    try:
        admin = Admin.objects.get(username=request.user)  # Get the admin object associated with the user
        context = {
            'admin': admin,
        }
        return render(request, 'admin_template/admin_profile.html', context)
    except Admin.DoesNotExist:
        # Handle the case when the user is not an admin
        return HttpResponse("You are not an admin.")

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


