from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User
from supabase import create_client
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import StudentProfile  # your model
from datetime import datetime


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
    student_user = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=student_user)

    # Count active courses (replace with your actual logic)
    active_courses_count = profile.courses.count() if hasattr(profile, 'courses') else 0

    context = {
        "student": student_user,
        "current_semester": "Fall 2025",  # or dynamically fetch
        "active_courses_count": active_courses_count,
        "gpa": profile.gpa or 0.0,
    }

    response = render(request, "StudentDashboard.html", context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

#@login_required(login_url='Login')#

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

#@login_required(login_url='Login')#
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

#@login_required(login_url='Login')#
def teacher_profile(request):
    context = {
        "first_name": "Robert",
        "last_name": "Smith",
        "email": "robert.smith@faculty.edu",
        "phone": "+1 (555) 987-6543",
        "address": "456 Faculty Building, University Campus",
        "dob": "June 20, 1975",
        "bio": "Professor of Computer Science with expertise in AI and Machine Learning. Published researcher with 15 years teaching experience.",
        "teacher_id": "FAC-2015-005678",
        "department": "Computer Science",
        "position": "Associate Professor",
        "office": "Room 405, CS Building",
        "office_hours": "MWF 10:00 AM - 12:00 PM",
    }
    return render(request, "TeacherProfile.html", context)

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

def teacher_base(request):
    return render(request, "teacher_base.html")
@login_required(login_url='Login')
@csrf_exempt
def update_student_profile(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    try:
        data = json.loads(request.body)
        user = request.user
        profile, _ = StudentProfile.objects.get_or_create(user=user)

        # --- Helpers ---
        def parse_date(date_str):
            if date_str:
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    return None
            return None

        def format_date(dt):
            return dt.strftime("%B %d, %Y") if dt else ""

        def safe_int(value, default=0):
            try:
                return int(float(value))
            except (TypeError, ValueError):
                return default

        def safe_float(value, default=0.0):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        # --- Update User fields ---
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.save()

        # --- Update StudentProfile fields ---
        profile.phone = data.get('phone', profile.phone)
        profile.address = data.get('address', profile.address)
        profile.dob = parse_date(data.get('dob')) or profile.dob
        profile.bio = data.get('bio', profile.bio)
        profile.program = data.get('major') or profile.program
        profile.year_level = safe_int(data.get('academic_year'), profile.year_level)
        profile.gpa = safe_float(data.get('gpa'), profile.gpa)
        profile.credits_completed = safe_int(data.get('credits_completed'), profile.credits_completed)
        profile.credits_required = safe_int(data.get('credits_required'), profile.credits_required)
        profile.academic_standing = data.get('academic_standing', profile.academic_standing)
        profile.expected_graduation = parse_date(data.get('expected_graduation')) or profile.expected_graduation

        profile.save()

        # --- Return JSON with formatted dates for display ---
        return JsonResponse({
            'status': 'success',
            'first_name': user.first_name or "",
            'last_name': user.last_name or "",
            'program': profile.program or "",
            'year_level': profile.year_level or 1,
            'dob': profile.dob.strftime("%Y-%m-%d") if profile.dob else "",
            'dob_display': format_date(profile.dob),
            'expected_graduation': profile.expected_graduation.strftime("%Y-%m-%d") if profile.expected_graduation else "",
            'expected_graduation_display': format_date(profile.expected_graduation),
            'credits_completed': profile.credits_completed or 0,
            'credits_required': profile.credits_required or 0,
            'gpa': profile.gpa or 0.0,
            'academic_standing': profile.academic_standing or "Good Standing"
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required(login_url='Login')
def student_profile(request):
    student_user = request.user

    profile, _ = StudentProfile.objects.get_or_create(user=student_user)

    # Calculate progress
    credits_completed = profile.credits_completed or 0
    credits_max = profile.credits_required or 0
    progress_percentage = (credits_completed / credits_max) * 100 if credits_max else 0

    # Helper to format date for display
    def format_date(dt):
        return dt.strftime("%B %d, %Y") if dt else ""

    context = {
        "first_name": student_user.first_name,
        "last_name": student_user.last_name,
        "email": student_user.email,
        "phone": profile.phone or "",
        "address": profile.address or "",
        "dob": profile.dob or "",
        "dob_display": format_date(profile.dob),
        "bio": profile.bio or "",
        "student_id": student_user.id_number,
        "major": profile.program or "",
        "academic_year": profile.year_level or 1,
        "expected_graduation": profile.expected_graduation or "",
        "expected_graduation_display": format_date(profile.expected_graduation),
        "gpa": profile.gpa or 0,
        "credits_completed": credits_completed,
        "credits_max": credits_max,
        "progress_percentage": progress_percentage,
        "achievements": profile.achievements.all(),

        # Sidebar
        "sidebar_program": profile.program or "",
        "sidebar_year": profile.year_level or "",
    }

    return render(request, "StudentProfile.html", context)

    student_user = request.user

    try:
        profile = student_user.studentprofile
    except StudentProfile.DoesNotExist:
        profile = StudentProfile.objects.create(user=student_user)

    # Calculate progress
    credits_completed = profile.credits_completed or 0
    credits_max = profile.credits_required or 0
    progress_percentage = (credits_completed / credits_max) * 100 if credits_max else 0

    context = {
    "first_name": student_user.first_name,
    "last_name": student_user.last_name,
    "email": student_user.email,
    "phone": profile.phone or "",
    "address": profile.address or "",
    "dob": profile.dob or "",
    "bio": profile.bio or "",
    "student_id": student_user.id_number,
    "major": profile.program,
    "academic_year": profile.year_level,
    "expected_graduation": profile.expected_graduation,
    "gpa": profile.gpa or 0,
    "credits_completed": credits_completed,
    "credits_max": credits_max,
    "progress_percentage": progress_percentage,
    "achievements": profile.achievements.all(),
    
    # Sidebar variables
    "sidebar_program": profile.program or "",
    "sidebar_year": profile.year_level or "",
}
   
    
    return render(request, "StudentProfile.html", context)

    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    try:
        data = json.loads(request.body)
        user = request.user
        profile, _ = StudentProfile.objects.get_or_create(user=user)

        # --- Update User fields ---
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.save()

        # --- Helper function for date conversion ---
        def parse_date(date_str):
            if date_str:
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    return None
            return None

        # --- Update StudentProfile fields ---
        profile.phone = data.get('phone', profile.phone)
        profile.address = data.get('address', profile.address)
        profile.dob = parse_date(data.get('dob')) or profile.dob
        profile.bio = data.get('bio', profile.bio)
        profile.program = data.get('program') or profile.program
        profile.year_level = int(data['year_level']) if 'year_level' in data and data['year_level'] else profile.year_level
        profile.gpa = float(data['gpa']) if 'gpa' in data and data['gpa'] else profile.gpa
        profile.credits_completed = int(float(data['credits_completed'])) if 'credits_completed' in data and data['credits_completed'] else profile.credits_completed
        profile.credits_required = int(float(data['credits_required'])) if 'credits_required' in data and data['credits_required'] else profile.credits_required
        profile.academic_standing = data.get('academic_standing', profile.academic_standing)
        profile.expected_graduation = parse_date(data.get('expected_graduation')) or profile.expected_graduation

        profile.save()

        # --- Return JSON response with formatted dates ---
        return JsonResponse({
            'status': 'success',
            'first_name': user.first_name or "",
            'last_name': user.last_name or "",
            'program': profile.program or "",
            'year_level': profile.year_level  or 0,
            'dob': profile.dob.strftime("%Y-%m-%d") if profile.dob else "",
            'expected_graduation': profile.expected_graduation.strftime("%Y-%m-%d") if profile.expected_graduation else "",
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user
            profile, _ = StudentProfile.objects.get_or_create(user=user)

            # Update User
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.email = data.get('email', user.email)
            user.save()

            # Update StudentProfile fields
            profile.phone = data.get('phone', profile.phone)
            profile.address = data.get('address', profile.address)
            profile.dob = data.get('dob') or profile.dob
            profile.bio = data.get('bio', profile.bio)
            profile.program = data.get('program') or profile.program
            profile.dob = data.get('dob') or profile.dob



            # Convert numeric fields safely
            if 'year_level' in data:
                profile.year_level = int(data['year_level'])

            if 'gpa' in data:
                profile.gpa = float(data['gpa'])

            if 'credits_completed' in data:
                profile.credits_completed = int(float(data['credits_completed']))

            if 'credits_required' in data:
                profile.credits_required = int(float(data['credits_required']))

            profile.academic_standing = data.get('academic_standing', profile.academic_standing)
            profile.expected_graduation = data.get('expected_graduation') or profile.expected_graduation

            profile.save()

            return JsonResponse({
                'status': 'success',
                'first_name': user.first_name,
                'last_name': user.last_name,
                'program': profile.program,
                'year_level': profile.year_level,
                'dob': profile.dob.strftime("%Y-%m-%d") if profile.dob else "",
                'expected_graduation': profile.expected_graduation.strftime("%Y-%m-%d") if profile.expected_graduation else "",
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user
            profile = user.studentprofile

            # Update User fields
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.email = data.get('email', user.email)
            user.save()

            # Update StudentProfile fields
            profile.phone = data.get('phone', profile.phone)
            profile.address = data.get('address', profile.address)
            profile.dob = data.get('dob', profile.dob)
            profile.bio = data.get('bio', profile.bio)
            profile.program = data.get('program', profile.program)
            profile.year_level = data.get('year_level', profile.year_level)
            profile.gpa = data.get('gpa', profile.gpa)
            profile.credits_completed = data.get('credits_completed', profile.credits_completed)
            profile.credits_required = data.get('credits_required', profile.credits_required)
            profile.academic_standing = data.get('academic_standing', profile.academic_standing)
            profile.expected_graduation = data.get('expected_graduation', profile.expected_graduation)
            profile.save()

            return JsonResponse({'status': 'success', 'message': 'Profile updated successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
