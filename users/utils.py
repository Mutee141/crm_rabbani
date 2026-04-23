def gm_required(view_func):
    from functools import wraps
    from django.shortcuts import redirect
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # We check the role string directly to avoid importing Models
        try:
            if hasattr(request.user, 'profile') and request.user.profile.role == 'GM':
                return view_func(request, *args, **kwargs)
        except Exception:
            pass
            
        return redirect('login')
    return wrapper

def hr_required(view_func):
    from functools import wraps
    from django.shortcuts import redirect
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        try:
            if hasattr(request.user, 'profile') and request.user.profile.role == 'HR':
                return view_func(request, *args, **kwargs)
        except Exception:
            pass
            
        return redirect('login')
    return wrapper