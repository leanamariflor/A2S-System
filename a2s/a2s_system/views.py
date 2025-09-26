from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate using email (custom user model)
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            if user.is_student:
                return redirect("StudentDashboard")
            elif user.is_teacher:
                return redirect("TeacherDashboard")
            else:
                messages.error(request, "User role not defined")
        else:
            messages.error(request, "Invalid email or password")
    return render(request, "Login.html")


def register(request):
    if request.method == "POST":
        id_number = request.POST.get("id_number")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        program = request.POST.get("program")
        yearlevel = request.POST.get("yearlevel")

        # Check required fields
        if not all([id_number, first_name, last_name, email, password, password2]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("register")

        # Password match
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        # Check unique email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        # Create the user
        user = User.objects.create_user(
            id_number=id_number,
            username=email,  # username is required in Django auth
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_student=True,
        )

        # Optional: assign program/yearlevel to student profile if exists
        if hasattr(user, "studentprofile"):
            user.studentprofile.program = program
            user.studentprofile.yearlevel = yearlevel
            user.studentprofile.save()

        messages.success(request, "Account created successfully! You can now login.")
        return redirect("login")

    return render(request, "Register.html")


@login_required
def student_dashboard(request):
    return render(request, "StudentDashboard.html")


@login_required
def teacher_dashboard(request):
    return render(request, "TeacherDashboard.html")


def logout_view(request):
    logout(request)
    return redirect("login")

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

