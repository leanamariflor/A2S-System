from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from supabase import create_client
from datetime import datetime, date, timedelta
import json
import os

from .models import StudentProfile, Enrollment, Grade,Schedule
from students.models import Curriculum
from authentication.models import User



# -----------------------------
# Supabase Setup
# -----------------------------
SUPABASE_URL = "https://qimrryerxdzfewbkoqyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpbXJyeWVyeGR6ZmV3YmtvcXlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4OTkyMjYsImV4cCI6MjA3NDQ3NTIyNn0.RYUzh-HS52HbiMGWhQiGkcf9OY0AeRsm0fuXruw0sEc"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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
        "current_semester": current_semester,  
    }

    return render(request, "students/StudentDashboard.html", context)


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
    return render(request, "students/StudentProfile.html", context)


@login_required(login_url="Login")
def student_schedule(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    enrollments = Enrollment.objects.filter(student=profile).order_by("schedule_day", "start_time")

    schedule_by_day = {}
    for e in enrollments:
        schedule_by_day.setdefault(e.schedule_day, []).append(e)

    return render(request, "students/StudentSchedule.html", {"schedule_by_day": schedule_by_day})


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

    return render(request, "students/StudentCourses.html", context)

@login_required(login_url="Login")
def student_curriculum(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    enrollments = Enrollment.objects.filter(student=profile).select_related("course")
    return render(request, "students/StudentCurriculum.html", {"enrollments": enrollments})


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

    return render(request, "students/StudentGrades.html", {
        "grades": grades,
        "years": years,
        "semesters": semesters,
        "selected_year": selected_year,
        "selected_semester": selected_sem,
    })


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


def student_base(request):
    return render(request, "students/student_base.html")


def get_curriculum_json(request, program):
    try:
        curriculum = Curriculum.objects.get(program__iexact=program)
        return JsonResponse(curriculum.data, safe=False)
    except Curriculum.DoesNotExist:
        return JsonResponse({'error': f'No curriculum found for {program}'}, status=404)
    

    

def student_schedule_json(request, student_id):
    student_profile = StudentProfile.objects.get(id=student_id)
    enrollments = Enrollment.objects.filter(student=student_profile)

    schedule = []
    for e in enrollments:
        schedule.append({
            "code": e.course.course_code,
            "section": getattr(e.course, 'section', 'N/A'),
            "room": getattr(e, 'room', 'N/A'),
            "time": f"{e.schedule_day} {e.start_time.strftime('%I:%M%p')}-{e.end_time.strftime('%I:%M%p')}"
        })

    return JsonResponse({"student_id": student_id, "schedule": schedule})



def student_schedule(request):
    days = ['M', 'T', 'W', 'TH', 'F', 'SAT']

    # Generate time slots as strings
    start_time = datetime.strptime("07:00 AM", "%I:%M %p")
    end_time = datetime.strptime("09:00 PM", "%I:%M %p")
    hours = []
    current = start_time
    while current <= end_time:
        hours.append(current.strftime("%I:%M %p"))
        current += timedelta(minutes=30)

    # Fetch schedules
    raw_scheds = Schedule.objects.filter(student__user=request.user)

    # Build a grid keyed by day and every half-hour slot
    schedule_grid = {day: {} for day in days}

    for s in raw_scheds:
        day = s.day.strip().upper()
        start_dt = datetime.combine(datetime.today(), s.time_start)
        end_dt = datetime.combine(datetime.today(), s.time_end)

        blocks = int((end_dt - start_dt).total_seconds() // (30 * 60))
        # Fill every 30-min slot for this course
        current_dt = start_dt
        for i in range(blocks):
            time_str = current_dt.strftime("%I:%M %p")
            # Only set the first block with course info, the rest will be marked as occupied
            if i == 0:
                schedule_grid[day][time_str] = {
                    'code': s.code,
                    'section': s.section,
                    'room': s.room,
                    'blocks': blocks,
                }
            else:
                schedule_grid[day][time_str] = {'occupied': True}
            current_dt += timedelta(minutes=30)

    context = {
        'days': days,
        'hours': hours,
        'schedule_grid': schedule_grid,
    }
    return render(request, 'students/StudentSchedule.html', context)
