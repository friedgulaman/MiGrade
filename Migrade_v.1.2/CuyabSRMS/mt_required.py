from functools import wraps
from django.shortcuts import redirect
from .views import ShowLoginPage

def mt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 4:
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to a login page or show an access denied message
            return redirect('ShowLoginPage')  # Replace 'login' with the name or URL of your login page
    return _wrapped_view
