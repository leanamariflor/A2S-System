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


# ----------------------------------------------------------------------
# Supabase Configuration & Constants
# ----------------------------------------------------------------------
SUPABASE_URL = "https://qimrryerxdzfewbkoqyq.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpbXJyeWVyeGR6ZmV3YmtvcXlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODg5OTIyNiwiZXhwIjoyMDc0NDc1MjI2fQ.b8Q1La_ZM8YSm6yt8Hw2qvNRS9GDkaLcbHWpb3ZK9eM"
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
DEFAULT_PIC_URL = f"{SUPABASE_URL}/storage/v1/object/public/ProfilePicture/avatar.png"


# ----------------------------------------------------------------------
# Base View
# ----------------------------------------------------------------------
@login_required(login_url="Login")
def student_base(request):
    return render(request, "students/student_base.html")


# ----------------------------------------------------------------------
# Student Dashboard & Profile Views
# ----------------------------------------------------------------------
@login_required(login_url="Login")
def student_dashboard(request):
    student_user = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=student_user)
    student_program = profile.program or "Undeclared"

    curriculum_data, calendar_data, current_courses = [], [], []

    # Progress calculation variables
    total_units = 0
    completed_units = 0
    completion_percentage = 0.0
    credits_remaining = 0
    current_gpa = float(profile.gpa) if profile.gpa else 0.0

    try:
        if student_program != "Undeclared":
            curriculum_obj = Curriculum.objects.get(program=student_program)
            curriculum_data = curriculum_obj.data.get("curriculum", [])

            # Calculate progress metrics
            for year in curriculum_data:
                for term in year.get("terms", []):
                    for subject in term.get("subjects", []):
                        units = subject.get('units', 3)
                        total_units += units
                        status = subject.get('final_grade', 'RECOMMENDED')
                        if status.upper() == 'PASSED':
                            completed_units += units

            if total_units > 0:
                completion_percentage = round((completed_units / total_units * 100), 1)
            credits_remaining = total_units - completed_units

            # Get current courses
            for year in curriculum_data:
                for term in year.get("terms", []):
                    for subj in term.get("subjects", []):
                        if subj.get("final_grade", "").upper() == "CURRENT":
                            current_courses.append(subj)
    except Curriculum.DoesNotExist:
        pass

    calendar_path = os.path.join(settings.BASE_DIR, "static", "data", "academic_calendar.json")
    try:
        with open(calendar_path, "r", encoding="utf-8") as f:
            calendar_data = json.load(f)
    except Exception as e:
        print("Error loading academic calendar:", e)

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
        # Progress overview data
        "total_units": total_units,
        "completed_units": completed_units,
        "completion_percentage": completion_percentage,
        "credits_remaining": credits_remaining,
        "current_gpa": current_gpa,
        "profile": profile,
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
    if profile.profile_picture:
        profile_picture_url = profile.profile_picture
    else:
        profile_picture_url = "https://qimrryerxdzfewbkoqyq.supabase.co/storage/v1/object/public/ProfilePicture/avatar.png"

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
        "profile_picture_url": profile_picture_url,
    }
    return render(request, "students/StudentProfile.html", context)


@csrf_exempt 
@login_required(login_url="Login")
def update_student_profile(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            user = request.user
            student = StudentProfile.objects.get(user=user)

            user.first_name = data.get("first_name", user.first_name)
            user.last_name = data.get("last_name", user.last_name)
            user.email = data.get("email", user.email)
            user.save()

            student.phone = data.get("phone", student.phone)
            student.address = data.get("address", student.address)
            student.bio = data.get("bio", student.bio)
            student.program = data.get("major", student.program)
            student.year_level = data.get("academic_year", student.year_level)
            student.gpa = data.get("gpa", student.gpa)
            student.credits_completed = data.get("credits_completed", student.credits_completed)
            student.academic_standing = data.get("academic_standing", student.academic_standing)
            student.save()

            return JsonResponse({"status": "success"})
        except Exception as e:
            print("❌ ERROR updating profile:", e)
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)


@csrf_exempt
@login_required
def upload_profile_picture(request):
    if request.method != 'POST' or 'file' not in request.FILES:
        return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)

    file = request.FILES['file']
    user = request.user

    try:
        profile, _ = StudentProfile.objects.get_or_create(user=user)
        file_path = f"{user.id}/{file.name}"
        file_bytes = file.read()

        upload_result = supabase.storage.from_('ProfilePicture').upload(file_path, file_bytes)

        if hasattr(upload_result, 'error') and upload_result.error is not None:
            raise Exception(f"Supabase upload error: {upload_result.error}")

        url_result = supabase.storage.from_('ProfilePicture').get_public_url(file_path)
        public_url = getattr(url_result, 'public_url', None) or getattr(url_result, 'url', None)

        if not public_url:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/ProfilePicture/{file_path}"

        profile.profile_picture = public_url
        profile.save(update_fields=['profile_picture'])

        return JsonResponse({'status': 'success', 'url': public_url})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def reset_profile_picture(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    default_url = "https://qimrryerxdzfewbkoqyq.supabase.co/storage/v1/object/public/ProfilePicture/avatar.png"
    profile.profile_picture = default_url
    profile.save(update_fields=['profile_picture'])
    return JsonResponse({'status': 'success', 'url': default_url})


# ----------------------------------------------------------------------
# Schedule & Course Enrollment Views
# ----------------------------------------------------------------------
@login_required(login_url="Login")
def student_schedule(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    enrollments = Enrollment.objects.filter(student=profile).order_by("schedule_day", "start_time")

    schedule_by_day = {}
    for e in enrollments:
        schedule_by_day.setdefault(e.schedule_day, []).append(e)

    return render(request, "students/StudentSchedule.html", {"schedule_by_day": schedule_by_day})


@login_required(login_url="Login")
def student_schedule(request):
    days = ['M', 'T', 'W', 'TH', 'F', 'SAT']

    start_time = datetime.strptime("07:00 AM", "%I:%M %p")
    end_time = datetime.strptime("09:00 PM", "%I:%M %p")
    hours = []
    current = start_time
    while current <= end_time:
        hours.append(current.strftime("%I:%M %p"))
        current += timedelta(minutes=30)

    raw_scheds = Schedule.objects.filter(student__user=request.user)

    schedule_grid = {day: {} for day in days}

    for s in raw_scheds:
        day = s.day.strip().upper()
        start_dt = datetime.combine(datetime.today(), s.time_start)
        end_dt = datetime.combine(datetime.today(), s.time_end)

        blocks = int((end_dt - start_dt).total_seconds() // (30 * 60))
        current_dt = start_dt
        for i in range(blocks):
            time_str = current_dt.strftime("%I:%M %p")
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


@login_required(login_url="Login")
def student_curriculum(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    enrollments = Enrollment.objects.filter(student=profile).select_related("course")
    return render(request, "students/StudentCurriculum.html", {"enrollments": enrollments})


@login_required(login_url='Login')
def student_courses(request):
    
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

                prelim_end = next((datetime.strptime(e["date"], "%Y-%m-%d").date() for e in events if "Prelim Examinations" in e["name"]), None)
                midterm_end = next((datetime.strptime(e["date"], "%Y-%m-%d").date() for e in events if "Midterm Examinations" in e["name"]), None)
                finals_end = end

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


# ----------------------------------------------------------------------
# Degree Audit & Grades Views
# ----------------------------------------------------------------------
@login_required(login_url='Login')
def student_degree_audit(request):
    student_user = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=student_user)
    student_program = profile.program if profile.program and profile.program != "Undeclared" else None

    curriculum_data = []
    all_courses = []
    completed_courses = []
    in_progress_courses = []
    not_started_courses = []
    
    gen_ed_courses = []
    major_core_courses = []
    elective_courses = []
    minor_courses = []
    
    total_units = 0
    completed_units = 0
    in_progress_units = 0
    
    if student_program:
        try:
            curriculum_obj = Curriculum.objects.get(program=student_program)
            curriculum_data = curriculum_obj.data.get("curriculum", [])
            
            for year in curriculum_data:
                for term in year.get("terms", []):
                    for subject in term.get("subjects", []):
                        course_info = {
                            'code': subject.get('subject_code', 'N/A'),
                            'title': subject.get('description', 'N/A'),
                            'units': subject.get('units', 3),
                            'semester': f"{year.get('year', '')} - {term.get('term', '')}",
                            'status': subject.get('final_grade', 'RECOMMENDED'),
                            'school_year': subject.get('school_year', ''),
                            'year': year.get('year', '')
                        }
                        
                        all_courses.append(course_info)
                        total_units += course_info['units']
                        
                        if course_info['status'] == 'PASSED':
                            completed_courses.append(course_info)
                            completed_units += course_info['units']
                        elif course_info['status'] == 'CURRENT':
                            in_progress_courses.append(course_info)
                            in_progress_units += course_info['units']
                        else:
                            not_started_courses.append(course_info)
                        
                        code = course_info['code'].upper()
                        
                        if any(prefix in code for prefix in ['GE', 'ENGL', 'MATH', 'PHILO', 'HUM', 'SOCSCI', 'NATSCI', 'HIST', 'PSYCH', 'PE', 'NSTP']):
                            gen_ed_courses.append(course_info)
                        elif 'ELEC' in code or 'ELCE' in code or 'FREEEL' in code:
                            elective_courses.append(course_info)
                        elif 'IT' in code or 'CSIT' in code or 'CS' in code:
                            major_core_courses.append(course_info)
                        else:
                            minor_courses.append(course_info)
                            
        except Curriculum.DoesNotExist:
            pass
    
    completion_percentage = (completed_units / total_units * 100) if total_units > 0 else 0
    credits_remaining = total_units - completed_units
    
    current_gpa = float(profile.gpa) if profile.gpa else 0.0
    
    achievements = profile.achievements.all()
    
    recommended_courses = []
    
    current_year_level = profile.year_level
    if curriculum_data and current_year_level <= len(curriculum_data):
        current_year_data = curriculum_data[current_year_level - 1] if current_year_level > 0 else None
        
        if current_year_data:
            for term in current_year_data.get('terms', []):
                for subject in term.get('subjects', []):
                    if subject.get('final_grade', '').upper() == 'RECOMMENDED':
                        recommended_courses.append({
                            'code': subject.get('subject_code', 'N/A'),
                            'title': subject.get('description', 'N/A'),
                            'units': subject.get('units', 3),
                            'semester': term.get('term', 'N/A')
                        })
    
    recommended_courses = recommended_courses[:6]
    
    calendar_path = os.path.join(settings.BASE_DIR, 'a2s', 'static', 'data', 'academic_calendar.json')
    current_semester = "Unknown Semester"
    try:
        with open(calendar_path, 'r', encoding='utf-8') as f:
            calendar_data = json.load(f)
            today = datetime.now().date()
            
            for sem in calendar_data:
                start_event = next((e for e in sem["events"] if "Start of Classes" in e["name"]), None)
                end_event = next((e for e in sem["events"] if "End of Classes" in e["name"]), None)
                
                if start_event and end_event:
                    start_date = datetime.strptime(start_event["date"], "%Y-%m-%d").date()
                    end_date = datetime.strptime(end_event["date"], "%Y-%m-%d").date()
                    
                    if start_date <= today <= end_date:
                        current_semester = sem["semester"]
                        break
    except Exception as e:
        print("Error loading academic calendar:", e)
    
    context = {
        'student': student_user,
        'profile': profile,
        'student_program': student_program or "No Program Assigned",
        'current_semester': current_semester,
        
        'total_units': total_units,
        'completed_units': completed_units,
        'in_progress_units': in_progress_units,
        'credits_remaining': credits_remaining,
        'completion_percentage': round(completion_percentage, 1),
        'current_gpa': current_gpa,
        
        'gen_ed_courses': gen_ed_courses,
        'major_core_courses': major_core_courses,
        'elective_courses': elective_courses,
        'minor_courses': minor_courses,
        
        'completed_courses': completed_courses,
        'in_progress_courses': in_progress_courses,
        'not_started_courses': not_started_courses,
        
        'achievements': achievements,
        'recommended_courses': recommended_courses,
        
        'all_courses_json': json.dumps([{
            'code': c['code'],
            'title': c['title'],
            'units': c['units']
        } for c in all_courses]),
    }
    
    return render(request, 'students/StudentDegreeAudit.html', context)


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


# ----------------------------------------------------------------------
# Utility and API Views (Progress, Curriculum, JSON)
# ----------------------------------------------------------------------
@login_required(login_url="Login")
def get_curriculum_json(request, program):
    try:
        curriculum = Curriculum.objects.get(program__iexact=program)
        return JsonResponse(curriculum.data, safe=False)
    except Curriculum.DoesNotExist:
        return JsonResponse({'error': f'No curriculum found for {program}'}, status=404)
    

@login_required(login_url="Login")
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


@login_required(login_url="Login")
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


@login_required(login_url="Login")
def calculate_subject_progress(semester_name, subject_status):
    if subject_status == "passed":
        return 100
    elif subject_status == "recommended":
        return 0
    elif subject_status == "current":
        with open("path/to/academic_calendar.json") as f:
            data = json.load(f)

        semester = next((s for s in data if s["semester"] == semester_name), None)
        if not semester:
            return 0

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


@login_required(login_url="Login")
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
                        "phase": e['name'].split()[0] 
                    }
    return {"semester": None, "phase": "Completed"}