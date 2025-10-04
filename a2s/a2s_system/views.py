from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User
from supabase import create_client

SUPABASE_URL = "https://qimrryerxdzfewbkoqyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpbXJyeWVyeGR6ZmV3YmtvcXlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4OTkyMjYsImV4cCI6MjA3NDQ3NTIyNn0.RYUzh-HS52HbiMGWhQiGkcf9OY0AeRsm0fuXruw0sEc"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember = request.POST.get("remember")

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            user_data = response.user
            if user_data is None:
                messages.error(request, "Invalid email or password.")
                return redirect("Login")

            if not user_data.email_confirmed_at:
                messages.warning(request, "Please verify your email before logging in.")
                return redirect("Login")

            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                response = redirect("StudentDashboard" if user.is_student else "TeacherDashboard")
                if remember:
                    response.set_cookie("remember_email", email, max_age=30 * 24 * 60 * 60)
                else:
                    response.delete_cookie("remember_email")
                return response
            else:
                messages.error(request, "Invalid login credentials.")
                return redirect("Login")

        except Exception as e:
            messages.error(request, f"Login error: {e}")
            return redirect("Login")

    remembered_email = request.COOKIES.get("remember_email", "")
    return render(request, "Login.html", {"remembered_email": remembered_email})

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
        role = request.POST.get("role")
        agree = request.POST.get("agree")

        if not all([id_number, first_name, last_name, email, password, password2, role]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("Register")

        if not agree:
            messages.error(request, "You must agree to the Terms of Service and Privacy Policy to register.")
            return redirect("Register")

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("Register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered in the system.")
            return redirect("Register")

        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            user_data = response.user
            if not user_data:
                messages.error(request, "Email already registered or pending verification. Please check your inbox.")
                return redirect("Register")

        except Exception as e:
            if "User already registered" in str(e) or "duplicate" in str(e).lower():
                messages.error(request, "Email already exists in Supabase. Please verify it or use another email.")
            else:
                messages.error(request, f"Supabase signup error: {e}")
            return redirect("Register")

        is_student = role.lower() == "student"
        is_teacher = role.lower() == "teacher"

        User.objects.create_user(
            id_number=id_number,
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_student=is_student,
            is_teacher=is_teacher,
        )

        messages.success(request, "Account created! A verification email has been sent — please verify before logging in.")
        return redirect("Login")

    return render(request, "Register.html")

@login_required(login_url='Login')
def student_dashboard(request):
    context = {}
    response = render(request, "StudentDashboard.html", context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required(login_url='Login')
def teacher_dashboard(request):
    context = {}
    response = render(request, "TeacherDashboard.html", context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def logout_view(request):
    logout(request)
    response = redirect('Login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

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

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email:
            messages.error(request, "Please enter your email.")
            return redirect("ForgotPassword")
        try:
            supabase.auth.reset_password_for_email(email)
            messages.success(request, "Password reset email sent! Check your inbox.")
            return redirect("Login")
        except Exception as e:
            messages.error(request, f"Error sending password reset email: {e}")
            return redirect("ForgotPassword")
    return render(request, "ForgotPassword.html")

def reset_password(request):
    return render(request, "ResetPassword.html")

def landing_page(request):
    return render(request, "LandingPage.html")


def settings(request):
    return render(request, "Settings.html")

def student_base(request):
    return render(request, "student_base.html")