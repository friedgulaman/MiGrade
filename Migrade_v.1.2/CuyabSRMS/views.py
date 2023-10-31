from .models import Teacher
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from .EmailBackEnd import EmailBackEnd  # Update the import path
from django.contrib import messages
from django.contrib.auth.decorators import login_required



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
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user = EmailBackEnd().authenticate(
            request, username=request.POST.get('email'), password=request.POST.get('password')
        )
        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # Check the user type and redirect accordingly
            if user.user_type == 2:  # Assuming '2' represents a teacher user type
                return redirect('home_teacher')
            else:
                return redirect('home_admin')
        else:
            messages.error(request, "Invalid Login Credentials!")
            return redirect('ShowLoginPage')
        
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
        return render(request, 'teacher_template/teacher_profile.html', context)
    else:
        # Handle the case for other user types (e.g., admin) or provide an error message
        return HttpResponse("You are not a teacher.")