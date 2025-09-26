from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate using email
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if user.is_student:
                return redirect("StudentDashboard")
            elif user.is_teacher:
                return redirect("TeacherDashboard")
            else:
                messages.error(request, "User role not defined")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # If you have a custom user model that uses email as username:
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("StudentDashboard")  # redirect for student
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Custom User: authenticate using email
        user = authenticate(request, username=email, password=password)  # or email field depending on your backend
        
        if user:
            login(request, user)
            return redirect("StudentDashboard")
        else:
            messages.error(request, "Invalid email or password")
    
    return render(request, "login.html")

# Registration (placeholder for now)
def register(request):
    return render(request, "register.html")

@login_required
def student_dashboard(request):
    return render(request, "StudentDashboard.html")

def teacher_dashboard(request):
    return render(request, "TeacherDashboard.html")

# Student profile (dummy data for now)
def student_profile(request):
    context = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@student.edu",
        "phone": "+1 (555) 123-4567",
        "address": "123 University Ave, Campus City",
        "dob": "May 15, 1999",
        "bio": "Computer Science student passionate about software development and AI.",
        "student_id": "CS-2021-001234",
        "major": "Computer Science",
        "minor": "Mathematics",
        "academic_year": "Senior",
        "expected_grad": "May 2025",
        "gpa": "3.85",
        "credits_completed": "105",
        "credits_max": "120",
    }
    return render(request, "StudentProfile.html", context)

# Logout view
def logout_view(request):
    logout(request)
    return redirect("login")
