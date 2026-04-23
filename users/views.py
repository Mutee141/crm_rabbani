from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from users.models import Profile

def login_view(request):
    # 1. Handle users who are already logged in
    if request.user.is_authenticated:
        try:
            role = request.user.profile.role
            if role == "HR": return redirect("hr:hr_dashboard")
            if role == "GM": return redirect("gm:dashboard")
            if role == "MANAGER": return redirect("manager:dashboard")
            if role == "TEAM_LEAD": return redirect("teamlead:dashboard")
            if role == "BDE": return redirect("bde:dashboard") # Future BDE
        except Exception:
            pass

    # 2. Handle Login Submission
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            profile = getattr(user, 'profile', None)
            
            if not profile:
                messages.error(request, f"Profile missing for {username}. Please contact Admin.")
                logout(request)
                return redirect("login")

            role = profile.role
            
            # Dashboard Redirect Logic
            if role == "HR":
                return redirect("hr:hr_dashboard")
            elif role == "GM":
                return redirect("gm:dashboard")
            elif role == "MANAGER":
                return redirect("manager:dashboard")
            elif role == "TEAM_LEAD":
                return redirect("teamlead:dashboard")
            elif role == "BDE":
                # Check if BDE app is created, else show warning
                try:
                    return redirect("bde:dashboard")
                except:
                    messages.warning(request, "BDE Dashboard is currently under construction.")
                    return redirect("login")
            else:
                messages.warning(request, f"Role '{role}' is not recognized.")
                return redirect("login")
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, "users/login.html")

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")