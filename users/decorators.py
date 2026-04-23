from django.shortcuts import redirect
from django.contrib import messages

def role_required(role_name):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Safe check for profile and role
            user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
            
            if user_role != role_name:
                messages.error(request, f"Access Denied: You do not have {role_name} permissions.")
                return redirect('login')
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator