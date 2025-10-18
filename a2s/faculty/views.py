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

from faculty.models import TeacherProfile
from students.models import Curriculum



# -----------------------------
# Supabase Setup
# -----------------------------
SUPABASE_URL = "https://qimrryerxdzfewbkoqyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpbXJyeWVyeGR6ZmV3YmtvcXlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4OTkyMjYsImV4cCI6MjA3NDQ3NTIyNn0.RYUzh-HS52HbiMGWhQiGkcf9OY0AeRsm0fuXruw0sEc"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


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



def teacher_base(request):
    return render(request, "teacher_base.html")



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
