from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from supabase import create_client
from datetime import datetime
from datetime import date

import json
import os

from .models import Course, TeacherProfile, User, StudentProfile, Enrollment, Curriculum, Grade


# -----------------------------
# Supabase Setup
# -----------------------------
SUPABASE_URL = "https://qimrryerxdzfewbkoqyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpbXJyeWVyeGR6ZmV3YmtvcXlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4OTkyMjYsImV4cCI6MjA3NDQ3NTIyNn0.RYUzh-HS52HbiMGWhQiGkcf9OY0AeRsm0fuXruw0sEc"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# -----------------------------
# Authentication Views
# -----------------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember = request.POST.get("remember")

        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user_data = response.user

            if not user_data:
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

        # --- Validation ---
        if not all([id_number, first_name, last_name, email, password, password2, role]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("Register")
        if not agree:
            messages.error(request, "You must agree to the Terms of Service.")
            return redirect("Register")
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("Register")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered in the system.")
            return redirect("Register")

        # --- Supabase registration ---
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            if not response.user:
                messages.error(request, "Email already registered or pending verification.")
                return redirect("Register")
        except Exception as e:
            messages.error(request, f"Supabase signup error: {e}")
            return redirect("Register")

        # --- Create local user ---
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

        messages.success(request, "Account created! Verify your email before logging in.")
        return redirect("Login")

    return render(request, "Register.html")


def logout_view(request):
    logout(request)
    response = redirect("Login")
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response

def forgot_password(request):
        return render(request, "ForgotPassword.html")

def reset_password(request):
        return render(request, "ResetPassword.html")

# -----------------------------
# Student Views
# -----------------------------
@login_required(login_url="Login")
def student_dashboard(request):
    student_user = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=student_user)
    student_program = profile.program or "Undeclared"

    curriculum_data, calendar_data, current_courses = [], [], []

    # --- Load Curriculum ---
    try:
        if student_program != "Undeclared":
            curriculum_obj = Curriculum.objects.get(program=student_program)
            curriculum_data = curriculum_obj.data.get("curriculum", [])
            for year in curriculum_data:
                for term in year.get("terms", []):
                    for subj in term.get("subjects", []):
                        if subj.get("final_grade", "").upper() == "CURRENT":
                            current_courses.append(subj)
    except Curriculum.DoesNotExist:
        pass

    # --- Load Academic Calendar ---
    calendar_path = os.path.join(settings.BASE_DIR, "a2s", "static", "data", "academic_calendar.json")
    try:
        with open(calendar_path, "r", encoding="utf-8") as f:
            calendar_data = json.load(f)
    except Exception as e:
        print("Error loading academic calendar:", e)

    # --- Determine Current Semester ---
    from datetime import date, datetime
    today = date.today()
    current_semester = "Unknown Semester"

    for sem in calendar_data:
        start_event = next((e for e in sem["events"] if "Start of Classes" in e["name"]), None)
        end_event = next((e for e in sem["events"] if "End of Classes" in e["name"]), None)

        if start_event and end_event:
            start_date = datetime.strptime(start_event["date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(end_event["date"], "%Y-%m-%d").date()

            if start_date <= today <= end_date:
                current_semester = sem["semester"]
                break

    context = {
        "student": student_user,
        "student_program": student_program,
        "curriculum_json": json.dumps(curriculum_data),
        "calendar_json": json.dumps(calendar_data),
        "current_courses": current_courses,
        "active_courses_count": len(current_courses),
        "gpa": profile.gpa or 0.0,
        "credits_completed": profile.credits_completed or 0,
        "credits_required": profile.credits_required or 0,
        "year_level": profile.year_level,
        "academic_standing": profile.academic_standing,
        "current_semester": current_semester,  # ✅ Added
    }

    return render(request, "StudentDashboard.html", context)


@login_required(login_url="Login")
def student_profile(request):
    user = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    credits_completed = profile.credits_completed or 0
    credits_max = profile.credits_required or 0
    progress = (credits_completed / credits_max) * 100 if credits_max else 0

    def format_date(dt):
        return dt.strftime("%B %d, %Y") if dt else ""

    context = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": profile.phone or "",
        "address": profile.address or "",
        "dob": profile.dob or "",
        "dob_display": format_date(profile.dob),
        "bio": profile.bio or "",
        "student_id": user.id_number,
        "major": profile.program or "",
        "academic_year": profile.year_level or 1,
        "expected_graduation": profile.expected_graduation or "",
        "expected_graduation_display": format_date(profile.expected_graduation),
        "gpa": profile.gpa or 0,
        "credits_completed": credits_completed,
        "credits_max": credits_max,
        "progress_percentage": progress,
        "achievements": profile.achievements.all(),
    }
    return render(request, "StudentProfile.html", context)


@login_required(login_url="Login")
def student_schedule(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    enrollments = Enrollment.objects.filter(student=profile).order_by("schedule_day", "start_time")

    schedule_by_day = {}
    for e in enrollments:
        schedule_by_day.setdefault(e.schedule_day, []).append(e)

    return render(request, "StudentSchedule.html", {"schedule_by_day": schedule_by_day})


@login_required(login_url='Login')
def student_courses(request):
    import json, os
    from datetime import datetime
    from django.conf import settings
    from .models import StudentProfile, Curriculum

    student_user = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=student_user)
    student_program = profile.program if profile.program and profile.program != "Undeclared" else None

    calendar_path = os.path.join(settings.BASE_DIR, 'a2s', 'static', 'data', 'academic_calendar.json')
    current_semester = None
    current_phase = None

    try:
        with open(calendar_path, 'r', encoding='utf-8') as f:
            academic_calendar = json.load(f)

        now = datetime.now().date()

        for sem in academic_calendar:
            events = sem.get("events", [])
            start = next((datetime.strptime(e["date"], "%Y-%m-%d").date() for e in events if "Start of Classes" in e["name"]), None)
            end = next((datetime.strptime(e["date"], "%Y-%m-%d").date() for e in events if "End of Classes" in e["name"]), None)

            if start and end and start <= now <= end:
                current_semester = sem.get("semester")

                # Determine phase
                prelim_end = next((datetime.strptime(e["date"], "%Y-%m-%d").date() for e in events if "Prelim Examinations" in e["name"]), None)
                midterm_end = next((datetime.strptime(e["date"], "%Y-%m-%d").date() for e in events if "Midterm Examinations" in e["name"]), None)
                finals_end = end

                # Determine phase more accurately
                if start and prelim_end and start <= now <= prelim_end:
                    current_phase = "Prelim"
                elif prelim_end and midterm_end and prelim_end < now <= midterm_end:
                    current_phase = "Midterm"
                elif midterm_end and end and midterm_end < now <= end:
                    current_phase = "Finals"
                elif end and now > end:
                    current_phase = "Completed"
                else:
                    current_phase = "Before Semester"

                
    except Exception as e:
        print("Error reading academic calendar:", e)

    curriculum_data = []
    active_courses_count = 0
    if student_program:
        try:
            curriculum_obj = Curriculum.objects.get(program=student_program)
            curriculum_data = curriculum_obj.data.get("curriculum", [])
            for year in curriculum_data:
                for term in year.get("terms", []):
                    for sub in term.get("subjects", []):
                        if sub.get("final_grade") == "CURRENT":
                            active_courses_count += 1
        except Curriculum.DoesNotExist:
            pass

    context = {
        "student": student_user,
        "student_program": student_program or "No program assigned",
        "curriculum_json": json.dumps(curriculum_data),
        "current_semester": current_semester or "No Active Semester",
        "current_phase": current_phase or "N/A",
        "current_year": datetime.now().year,
        "active_courses": active_courses_count,
    }

    return render(request, "StudentCourses.html", context)

@login_required(login_url="Login")
def student_curriculum(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    enrollments = Enrollment.objects.filter(student=profile).select_related("course")
    return render(request, "StudentCurriculum.html", {"enrollments": enrollments})


@login_required(login_url="Login")
def student_grades(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    selected_year = request.GET.get("school_year")
    selected_sem = request.GET.get("semester")

    grades = Grade.objects.none()
    years = Grade.objects.filter(student=profile).values_list("school_year", flat=True).distinct()
    semesters = Grade.objects.filter(student=profile).values_list("semester", flat=True).distinct()

    if selected_year and selected_sem:
        grades = Grade.objects.filter(student=profile, school_year=selected_year, semester=selected_sem)

    return render(request, "StudentGrades.html", {
        "grades": grades,
        "years": years,
        "semesters": semesters,
        "selected_year": selected_year,
        "selected_semester": selected_sem,
    })


# -----------------------------
# Teacher Views
# -----------------------------

@login_required(login_url="Login")
def teacher_dashboard(request):
    teacher_user = request.user

    # --- Get Teacher Profile ---
    try:
        profile = TeacherProfile.objects.get(user=teacher_user)
    except TeacherProfile.DoesNotExist:
        profile = None

    # --- Load Academic Calendar ---
    calendar_data = []
    calendar_path = os.path.join(settings.BASE_DIR, "a2s", "static", "data", "academic_calendar.json")

    try:
        with open(calendar_path, "r", encoding="utf-8") as f:
            calendar_data = json.load(f)
    except Exception as e:
        print("Error loading academic calendar:", e)
        calendar_data = []

    # --- Determine Current Semester ---
    current_semester = "Unknown Semester"
    today = date.today()

    for sem in calendar_data:
        start_event = next((e for e in sem["events"] if "Start of Classes" in e["name"]), None)
        end_event = next((e for e in sem["events"] if "End of Classes" in e["name"]), None)

        if start_event and end_event:
            start_date = datetime.strptime(start_event["date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(end_event["date"], "%Y-%m-%d").date()

            if start_date <= today <= end_date:
                current_semester = sem["semester"]
                break

    # --- Stats ---
    total_courses = Course.objects.filter(grade__faculty=teacher_user.get_full_name()).distinct().count()
    total_students = Enrollment.objects.filter(course__grade__faculty=teacher_user.get_full_name()).count()

    # --- Context Data ---
    context = {
        "teacher": teacher_user,
        "first_name": teacher_user.first_name,
        "last_name": teacher_user.last_name,
        "department": profile.department if profile else "N/A",
        "position": profile.position if profile else "N/A",
        "total_courses": total_courses,
        "total_students": total_students,
        "calendar_json": json.dumps(calendar_data),
        "current_semester": current_semester,
    }

    return render(request, "TeacherDashboard.html", context)

COLLEGE_CHOICES = [
    ("CEA", "Engineering and Architecture"),
    ("CCS", "Computer Studies"),
    ("CASE", "Arts, Sciences and Education"),
    ("CMBA", "Management, Business and Accountancy"),
    ("CNAHS", "Nursing and Allied Health Sciences"),
    ("CCJ", "Criminal Justice"),
]

POSITION_CHOICES = [
    "Full-Time Faculty",
    "Part-Time Faculty",
    "Visiting Lecturer",
    "Adjunct Faculty",
]

@login_required(login_url="Login")
def teacher_profile(request):
    user = request.user
    profile, _ = TeacherProfile.objects.get_or_create(user=user)

    def format_date(dt):
        return dt.strftime("%B %d, %Y") if dt else ""

    total_courses = Course.objects.filter(grade__faculty=user.get_full_name()).distinct().count()
    total_students = Enrollment.objects.filter(course__grade__faculty=user.get_full_name()).count()

    context = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": profile.phone or "",
        "address": profile.address or "",
        "dob": profile.dob or "",
        "dob_display": format_date(profile.dob),
        "bio": profile.bio or "",
        "department": profile.department or "",
        "specialization": profile.specialization or "",
        "teacher_id": user.id_number or "",
        "date_joined": format_date(user.date_joined),
        "total_courses": total_courses,
        "total_students": total_students,
        "achievements": profile.achievements.all(),
        "position": profile.position or "Full-Time Faculty",
        "college_choices": COLLEGE_CHOICES,
        "position_choices": POSITION_CHOICES,
    }
    return render(request, "TeacherProfile.html", context)



@login_required(login_url="Login")
def teacher_courses(request):
    teacher = request.user
    courses_data = {}

    file_path = os.path.join(settings.BASE_DIR, "a2s", "static", "data", "teacher_courses.json")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            courses_data = json.load(f)
    except Exception as e:
        print("Error loading teacher_courses.json:", e)

    context = {
        "teacher_name": teacher.get_full_name(),
        "school_year": courses_data.get("school_year", "N/A"),
        "active_courses": courses_data.get("active_courses", 0),
        "courses": courses_data.get("courses", [])
    }

    return render(request, "TeacherCourses.html", context)


@login_required(login_url="Login")
def api_teacher_courses(request):
    """Return teacher courses as JSON for dynamic loading."""
    file_path = os.path.join(settings.BASE_DIR, "a2s", "static", "data", "teacher_courses.json")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        data = {"error": str(e)}

    return JsonResponse(data)

def teacher_progress_uploads(request):
    import json, os
    from django.conf import settings

    file_path = os.path.join(settings.BASE_DIR, "a2s", "static", "data", "student_progress_uploads.json")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return render(request, "teacher_courses.html", {"upload_data": data})

def course_grades(request, course_id):
    import json, os
    from django.conf import settings

    file_path = os.path.join(settings.BASE_DIR, "a2s", "static", "data", "student_grades.json")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Find course by ID
    course = next((c for c in data["courses"] if c["course_id"] == course_id), None)
    return render(request, "teacher_course_grades.html", {"course": course})

# -----------------------------
# Utility Views
# -----------------------------
@login_required(login_url="Login")
@csrf_exempt
def update_student_profile(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"})

    try:
        data = json.loads(request.body)
        user = request.user
        profile, _ = StudentProfile.objects.get_or_create(user=user)

        def parse_date(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d").date() if s else None
            except ValueError:
                return None

        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.email = data.get("email", user.email)
        user.save()

        profile.phone = data.get("phone", profile.phone)
        profile.address = data.get("address", profile.address)
        profile.dob = parse_date(data.get("dob")) or profile.dob
        profile.bio = data.get("bio", profile.bio)
        profile.program = data.get("major", profile.program)
        profile.year_level = data.get("academic_year", profile.year_level)
        profile.gpa = data.get("gpa", profile.gpa)
        profile.credits_completed = data.get("credits_completed", profile.credits_completed)
        profile.credits_required = data.get("credits_required", profile.credits_required)
        profile.academic_standing = data.get("academic_standing", profile.academic_standing)
        profile.expected_graduation = parse_date(data.get("expected_graduation")) or profile.expected_graduation
        profile.save()

        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


@csrf_exempt
@login_required
def update_teacher_profile(request):
    import json
    user = request.user
    profile = user.teacherprofile
    if request.method == "POST":
        data = json.loads(request.body)
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.save()
        profile.phone = data.get("phone", profile.phone)
        profile.address = data.get("address", profile.address)
        profile.dob = data.get("dob", profile.dob)
        profile.bio = data.get("bio", profile.bio)
        profile.department = data.get("department", profile.department)
        profile.specialization = data.get("specialization", profile.specialization)
        profile.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request"})

def get_curriculum_json(request, program):
    try:
        curriculum = Curriculum.objects.get(program=program)
        return JsonResponse({"curriculum": curriculum.data["curriculum"]}, safe=False)
    except Curriculum.DoesNotExist:
        return JsonResponse({"error": "Curriculum not found"}, status=404)


def user_settings(request):
    return render(request, "Settings.html")


def landing_page(request):
    return render(request, "LandingPage.html")


def student_base(request):
    return render(request, "student_base.html")


def teacher_base(request):
    return render(request, "teacher_base.html")


# -----------------------------
# Helpers
# -----------------------------
def calculate_semester_progress(calendar_data):
    today = datetime.now().date()
    for semester in calendar_data:
        events = semester.get("events", [])
        start = next((datetime.strptime(e["date"], "%Y-%m-%d").date() for e in events if e["type"] == "Class Start"), None)
        end = next((datetime.strptime(e["date"], "%Y-%m-%d").date() for e in events if e["type"] == "Class End"), None)
        if start and end and start <= today <= end:
            total = (end - start).days
            elapsed = (today - start).days
            return max(0, min(int((elapsed / total) * 100), 100))
    return 0


def calculate_subject_progress(semester_name, subject_status):
    if subject_status == "passed":
        return 100
    elif subject_status == "recommended":
        return 0
    elif subject_status == "current":
        with open("path/to/academic_calendar.json") as f:
            data = json.load(f)

        # Find semester data
        semester = next((s for s in data if s["semester"] == semester_name), None)
        if not semester:
            return 0

        # Get start and end dates
        start_event = next((e for e in semester["events"] if e["type"] == "Class Start"), None)
        end_event = next((e for e in semester["events"] if e["type"] == "Class End"), None)

        if not start_event or not end_event:
            return 0

        start_date = datetime.strptime(start_event["date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(end_event["date"], "%Y-%m-%d").date()
        today = date.today()

        if today < start_date:
            return 0
        elif today > end_date:
            return 100

        total_days = (end_date - start_date).days
        elapsed_days = (today - start_date).days
        progress = (elapsed_days / total_days) * 100
        return round(progress, 1)


def get_current_phase(academic_calendar):
    today = date.today()

    for sem in academic_calendar:
        events = sem['events']
        for e in events:
            if e['type'] == 'Exam':
                event_date = datetime.strptime(e['date'], "%Y-%m-%d").date()
                if today <= event_date:
                    return {
                        "semester": sem['semester'],
                        "phase": e['name'].split()[0]  # "Prelim", "Midterm", etc.
                    }
    return {"semester": None, "phase": "Completed"}