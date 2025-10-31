from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_GET
from django.http import HttpResponse

import json, os, csv
from datetime import datetime, timedelta, date

from supabase import create_client

from teacher.models import TeacherProfile, Schedule
from students.models import Curriculum, Course, Enrollment, StudentProfile
from students.models import CourseAssignment, Grade


# -----------------------------
# Supabase Setup
# -----------------------------
SUPABASE_URL = "https://qimrryerxdzfewbkoqyq.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpbXJyeWVyeGR6ZmV3YmtvcXlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODg5OTIyNiwiZXhwIjoyMDc0NDc1MjI2fQ.b8Q1La_ZM8YSm6yt8Hw2qvNRS9GDkaLcbHWpb3ZK9eM"
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
DEFAULT_PROFILE_URL = f"{SUPABASE_URL}/storage/v1/object/public/ProfilePicture/avatar.png"


# -----------------------------
# Constant Choices
# -----------------------------
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


# -----------------------------
# Base View
# -----------------------------
def teacher_base(request):
    return render(request, "teacher/teacher_base.html")


# -----------------------------
# Teacher Dashboard & Profile Views
# -----------------------------
@login_required(login_url="Login")
def teacher_dashboard(request):
    teacher_user = request.user

    try:
        profile = TeacherProfile.objects.get(user=teacher_user)
    except TeacherProfile.DoesNotExist:
        profile = None

    schedules = Schedule.objects.filter(teacher=profile).order_by("subject_code", "section")

    course_data = []
    total_students_all = set()

    for sched in schedules:
        course_code = sched.subject_code
        section = sched.section

        if "/" in section:
            continue

        student_ids = CourseAssignment.objects.filter(
            teacher=profile,
            course_code=course_code,
            section=section
        ).values_list("student_id", flat=True).distinct()

        student_count = len(student_ids)
        total_students_all.update(student_ids)

        course_data.append({
            "course_code": course_code,
            "section": section,
            "student_count": student_count,
        })

    seen = set()
    unique_courses = []
    for c in course_data:
        key = f"{c['course_code']}-{c['section']}"
        if key not in seen:
            unique_courses.append(c)
            seen.add(key)

    total_courses = len(unique_courses)
    total_students = len(total_students_all)

    calendar_data = []
    calendar_path = os.path.join(settings.BASE_DIR, "static", "data", "academic_calendar.json")
    try:
        with open(calendar_path, "r", encoding="utf-8") as f:
            calendar_data = json.load(f)
    except Exception:
        calendar_data = []

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

    context = {
        "teacher": teacher_user,
        "first_name": teacher_user.first_name,
        "last_name": teacher_user.last_name,
        "department": profile.department if profile else "N/A",
        "position": profile.position if profile else "N/A",
        "courses": unique_courses,
        "total_courses": total_courses,
        "total_students": total_students,
        "current_semester": current_semester,
        "calendar_json": json.dumps(calendar_data),
    }

    return render(request, "teacher/TeacherDashboard.html", context)


@login_required(login_url="Login")
def teacher_profile(request):
    user = request.user
    profile, _ = TeacherProfile.objects.get_or_create(user=user)

    def format_date(dt):
        return dt.strftime("%B %d, %Y") if dt else ""
    if profile.profile_picture:
        profile_picture_url = profile.profile_picture
    else:
        profile_picture_url = "https://qimrryerxdzfewbkoqyq.supabase.co/storage/v1/object/public/ProfilePicture/avatar.png"

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
        "profile_picture_url": profile_picture_url,

    }
    return render(request, "teacher/TeacherProfile.html", context)

@csrf_exempt
@login_required(login_url="Login")
def update_teacher_profile(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))
        user = request.user
        profile = user.teacherprofile

        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.email = data.get("email", user.email)
        user.save()

        profile.phone = data.get("phone", profile.phone)
        profile.address = data.get("address", profile.address)
        profile.bio = data.get("bio", profile.bio)
        profile.department = data.get("department", profile.department)
        profile.specialization = data.get("specialization", profile.specialization)
        profile.position = data.get("position", profile.position)
        profile.save()

        return JsonResponse({"status": "success"})
    except Exception as e:
        print("❌ ERROR updating teacher profile:", e)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



@csrf_exempt
@login_required
def upload_profile_picture(request):
    if request.method != 'POST' or 'file' not in request.FILES:
        return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)

    file = request.FILES['file']
    user = request.user

    try:
        profile, _ = TeacherProfile.objects.get_or_create(user=user)
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
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
    default_url = "https://qimrryerxdzfewbkoqyq.supabase.co/storage/v1/object/public/ProfilePicture/avatar.png"
    profile.profile_picture = default_url
    profile.save(update_fields=['profile_picture'])
    return JsonResponse({'status': 'success', 'url': default_url})



# -----------------------------
# Schedule & Course Views (List)
# -----------------------------
@login_required(login_url="Login")
def teacher_schedule(request):
    days = ['M', 'T', 'W', 'TH', 'F', 'SAT']

    start_time = datetime.strptime("07:00 AM", "%I:%M %p")
    end_time = datetime.strptime("09:00 PM", "%I:%M %p")
    hours = []
    current = start_time
    while current <= end_time:
        hours.append(current.strftime("%I:%M %p"))
        current += timedelta(minutes=30)

    teacher_profile = TeacherProfile.objects.get(user=request.user)
    raw_scheds = Schedule.objects.filter(teacher=teacher_profile)

    schedule_grid = {day: {} for day in days}

    for s in raw_scheds:
        day = s.day.strip().upper()
        start_dt = datetime.combine(datetime.today(), s.start_time)
        end_dt = datetime.combine(datetime.today(), s.end_time)
        blocks = int((end_dt - start_dt).total_seconds() // (30 * 60))
        current_dt = start_dt

        for i in range(blocks):
            time_str = current_dt.strftime("%I:%M %p")
            if i == 0:
                schedule_grid[day][time_str] = {
                    'code': s.subject_code,
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
    return render(request, 'teacher/TeacherSchedule.html', context)


@login_required(login_url="Login")
def teacher_courses(request):
    teacher_profile = TeacherProfile.objects.get(user=request.user)

    schedules = Schedule.objects.filter(teacher=teacher_profile).order_by("subject_code", "section")

    courses_list = []
    seen = set()
    for sched in schedules:
        if '/' in sched.section:
            continue

        key = f"{sched.subject_code}-{sched.section}"
        if key not in seen:
            courses_list.append({
                "course_code": sched.subject_code,
                "section": sched.section,
                "action": "view"
            })
            seen.add(key)

    courses_list.sort(key=lambda x: (x["course_code"], x["section"]))

    context = {
        "teacher_name": request.user.get_full_name(),
        "school_year": "2025-2026",
        "active_courses": len(courses_list),
        "courses": courses_list,
    }

    return render(request, "teacher/TeacherCourses.html", context)

@login_required(login_url="Login")
def my_course_advisees(request):
    teacher = request.user.teacherprofile
    assignments = teacher.student_assignments.all()
    return render(request, 'faculty/course_advisees.html', {'assignments': assignments})


# -----------------------------
# Course Class List & Students
# -----------------------------
@login_required(login_url="Login")
def teacher_classlist(request, course_code, section):
    try:
        response = supabase.table("students_courseassignment") \
            .select("id, course_code, section, student_id") \
            .eq("course_code", course_code) \
            .eq("section", section) \
            .execute()

        students_list = []

        if response.data:
            for sca in response.data:
                student_id = sca.get("student_id")

                student_profile = supabase.table("students_studentprofile") \
                    .select("user_id, program, year_level") \
                    .eq("id", student_id) \
                    .single().execute()

                if student_profile.data:
                    user_id = student_profile.data.get("user_id")

                    user_data = supabase.table("authentication_user") \
                        .select("first_name, last_name") \
                        .eq("id", user_id) \
                        .single().execute()

                    full_name = ""
                    if user_data.data:
                        full_name = f"{user_data.data.get('first_name', '')} {user_data.data.get('last_name', '')}"

                    students_list.append({
                        "id": sca["id"],
                        "full_name": full_name,
                        "program": student_profile.data.get("program"),
                        "year_level": student_profile.data.get("year_level"),
                    })

        context = {
            "course_code": course_code,
            "section": section,
            "students": students_list,
        }

        return render(request, "teacher/TeacherClassList.html", context)

    except Exception as e:
        print("Error fetching class list:", e)
        return render(request, "teacher/TeacherClassList.html", {
            "course_code": course_code,
            "section": section,
            "students": [],
            "error": str(e)
        })


@login_required(login_url="Login")
def student_status(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    teacher = request.user.teacherprofile

    user_data = supabase.table("authentication_user") \
        .select("first_name, last_name, username, id_number") \
        .eq("id", student.user_id) \
        .single().execute()

    full_name = ""
    username = ""
    student_number = ""
    if user_data.data:
        full_name = f"{user_data.data.get('first_name', '')} {user_data.data.get('last_name', '')}"
        username = user_data.data.get('username', '')
        student_number = user_data.data.get('id_number', '')

    teacher_assignments = CourseAssignment.objects.filter(student=student, teacher=teacher)
    teacher_courses = teacher_assignments.values_list("course_code", flat=True)

    grades = Grade.objects.filter(student=student, course_code__in=teacher_courses).values(
        "course_code", "course_name", "midterm", "final_grade", "remarks", "semester", "school_year"
    )

    course_code, section = "", ""
    first_assignment = teacher_assignments.first()
    if first_assignment:
        course_code = first_assignment.course_code
        section = first_assignment.section

    context = {
        "student": student,
        "full_name": full_name,
        "username": username,
        "student_number": student_number,
        "grades": grades,
        "course_code": course_code,
        "section": section,
        "student_id": student.id,
    }

    return render(request, "teacher/StudentStatus.html", context)


# -----------------------------
# Grade Management Views
# -----------------------------
@login_required(login_url="Login")
def add_grade(request, student_id, course_code):
    student = get_object_or_404(StudentProfile, id=student_id)

    assignment_exists = CourseAssignment.objects.filter(
        student=student,
        teacher=request.user.teacherprofile,
        course_code=course_code
    ).exists()

    if not assignment_exists:
        return HttpResponse("You are not assigned to this student for this course.", status=403)

    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.student = student
            grade.course_code = course_code
            grade.faculty = request.user.get_full_name()
            grade.save()
            return redirect('my_advisees')
    else:
        form = GradeForm()

    return render(request, 'faculty/add_grade.html', {'form': form, 'student': student, 'course_code': course_code})


@login_required(login_url="Login")
@csrf_exempt
def update_grade_notes(request):
    if request.method == "POST":
        data = json.loads(request.body)
        grade_id = data.get("grade_id")
        note_text = data.get("notes", "")

        try:
            grade = Grade.objects.get(id=grade_id, teacher=request.user.teacherprofile)
            grade.notes = note_text
            grade.save()
            return JsonResponse({"status": "success", "notes": grade.notes})
        except Grade.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Grade not found or permission denied."})

    return JsonResponse({"status": "error", "message": "Invalid request method."})


# -----------------------------
# Curriculum API View
# -----------------------------
@login_required(login_url="Login")
def get_curriculum_json(request, program):
    try:
        curriculum = Curriculum.objects.get(program=program)
        return JsonResponse({"curriculum": curriculum.data["curriculum"]}, safe=False)
    except Curriculum.DoesNotExist:
        return JsonResponse({"error": "Curriculum not found"}, status=404)


# -----------------------------
# Data Export Views
# -----------------------------
@login_required(login_url="Login")
def export_student_report(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    grades = student.grades.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{student.full_name}_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Course Code', 'Course Name', 'Midterm', 'Final Grade', 'Remarks', 'Semester', 'School Year'])
    for g in grades:
        writer.writerow([g.course_code, g.course_name, g.midterm, g.final_grade, g.remarks, g.semester, g.school_year])

    return response


@login_required(login_url="Login")
def export_student_report(request, student_id):
    teacher = request.user.teacherprofile
    student = get_object_or_404(StudentProfile, id=student_id)

    teacher_courses = CourseAssignment.objects.filter(
        student=student,
        teacher=teacher
    ).values_list("course_code", flat=True)

    grades = Grade.objects.filter(student=student, course_code__in=teacher_courses)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{student.user.get_full_name()}_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Course Code', 'Course Name', 'Midterm', 'Final Grade', 'Remarks', 'Semester', 'School Year'])

    for g in grades:
        writer.writerow([g.course_code, g.course_name, g.midterm, g.final_grade, g.remarks, g.semester, g.school_year])

    return response


# -----------------------------
# JSON API Views
# -----------------------------
@login_required(login_url="Login")
def api_teacher_courses(request):
    file_path = os.path.join(settings.BASE_DIR, "a2s", "static", "data", "teacher_courses.json")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        data = {"error": str(e)}

    return JsonResponse(data)


@login_required(login_url="Login")
def api_teacher_courses(request):
    teacher_id = request.user.id

    try:
        response = supabase.table("students_courseassignment") \
            .select("course_code, section") \
            .eq("teacher_id", teacher_id) \
            .execute()

        courses = []
        if response.data:
            seen = set()
            for item in response.data:
                key = f"{item['course_code']}-{item.get('section','')}"
                if key not in seen:
                    courses.append({
                        "course_code": item["course_code"],
                        "section": item.get("section", ""),
                    })
                    seen.add(key)

        return JsonResponse({"courses": courses}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required(login_url="Login")
@require_GET
def get_course_students(request, course_code, section):
    try:
        response = supabase.table("students_courseassignment") \
            .select("id, course_code, section, student_id") \
            .eq("course_code", course_code) \
            .eq("section", section) \
            .execute()

        students_list = []

        if response.data:
            for sca in response.data:
                student_id = sca.get("student_id")

                student_profile = supabase.table("students_studentprofile") \
                    .select("user_id, program, year_level") \
                    .eq("id", student_id) \
                    .single().execute()

                if student_profile.data:
                    user_id = student_profile.data.get("user_id")

                    user_data = supabase.table("authentication_user") \
                        .select("first_name, last_name") \
                        .eq("id", user_id) \
                        .single().execute()

                    full_name = ""
                    if user_data.data:
                        full_name = f"{user_data.data.get('first_name', '')} {user_data.data.get('last_name', '')}"

                    students_list.append({
                        "id": sca["id"],
                        "full_name": full_name,
                        "course_code": sca["course_code"],
                        "section": sca["section"],
                        "year_level": student_profile.data.get("year_level", ""),
                        "program": student_profile.data.get("program")
                    })

        return JsonResponse({"students": students_list})

    except Exception as e:
        print("Error fetching students:", e)
        return JsonResponse({"students": [], "error": str(e)}, status=500)