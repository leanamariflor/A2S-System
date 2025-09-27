from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User
from supabase import create_client

# Supabase client
SUPABASE_URL = "https://qimrryerxdzfewbkoqyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpbXJyeWVyeGR6ZmV3YmtvcXlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4OTkyMjYsImV4cCI6MjA3NDQ3NTIyNn0.RYUzh-HS52HbiMGWhQiGkcf9OY0AeRsm0fuXruw0sEc"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ------------------ LOGIN ------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not all([email, password]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("Login")

        try:
            # Supabase login
            supabase_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if supabase_response.user is None:
                messages.error(request, "Invalid email or password.")
                return redirect("Login")

            if not supabase_response.user.confirmed_at:
                messages.error(request, "Email not confirmed. Check your inbox for verification link.")
                return redirect("Login")

        except Exception as e:
            messages.error(request, f"Login error: {e}")
            return redirect("Login")

        # Django authentication
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            if user.is_student:
                return redirect("StudentDashboard")
            elif user.is_teacher:
                return redirect("TeacherDashboard")
            else:
                messages.error(request, "User role not defined.")
                return redirect("Login")
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("Login")

    return render(request, "Login.html")


# ------------------ REGISTER ------------------
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
        role = request.POST.get("role")  # "Student" or "Teacher"

        # --- Validation ---
        if not all([id_number, first_name, last_name, email, password, password2, role]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("Register")

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("Register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("Register")

        is_student = role.lower() == "student"
        is_teacher = role.lower() == "teacher"

        # --- Supabase signup ---
        try:
            supabase_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            user_data = supabase_response.user
            if user_data and not user_data.confirmed_at:
                messages.info(request, "Verification email sent. Please check your inbox.")

        except Exception as e:
            messages.error(request, f"Supabase signup error: {e}")
            return redirect("Register")

        # --- Django user creation ---
        user = User.objects.create_user(
            id_number=id_number,
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_student=is_student,
            is_teacher=is_teacher,
        )



        messages.success(request, "Account created! Verify your email before logging in.")
        return redirect("Login")

    return render(request, "Register.html")


# ------------------ DASHBOARDS ------------------
@login_required(login_url='Login')
def student_dashboard(request):
    context = {}
    response = render(request, "StudentDashboard.html", context)
    # Prevent caching
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@login_required(login_url='Login')
def teacher_dashboard(request):
    context = {}
    response = render(request, "TeacherDashboard.html", context)
    # Prevent caching
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# ------------------ LOGOUT ------------------
def logout_view(request):
    logout(request)
    response = redirect('Login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# ------------------ STUDENT PROFILE ------------------
@login_required(login_url='Login')
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
