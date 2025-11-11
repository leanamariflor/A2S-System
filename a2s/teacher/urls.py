from django.urls import path
from . import views

urlpatterns = [

    # Teacher Dashboard & Profile
   
    path('TeacherDashboard/', views.teacher_dashboard, name='TeacherDashboard'),
    path('TeacherProfile/', views.teacher_profile, name='TeacherProfile'),
    path('UpdateTeacherProfile/', views.update_teacher_profile, name='UpdateTeacherProfile'),
    path('teacher_base/', views.teacher_base, name='teacher_base'),
    path('upload-profile-picture/', views.upload_profile_picture, name='UploadProfilePicture'),
    path('reset-profile-picture/', views.reset_profile_picture, name='reset_profile_picture'),

    path('teacher_notifications/', views.teacher_get_notifications, name='teacher_get_notifications'),
    path('teacher_notifications/read/', views.teacher_mark_notification_read, name='teacher_mark_notification_read'),
    path("academic-calendar/", views.academic_calendar, name="academic-calendar"),
   
    # Teacher Courses & Schedule
    path('TeacherGrades/', views.teacher_grades, name='TeacherGrades'),

    path('TeacherCourses/', views.teacher_courses, name='TeacherCourses'),
    path('TeacherSchedule/', views.teacher_schedule, name='TeacherSchedule'),
    path('TeacherClassList/<str:course_code>/<str:section>/', views.teacher_classlist, name='teacher_classlist'),
    path('TeacherGradesList/<str:course_code>/<str:section>/', views.teacher_grades_list, name='teacher_grades_list'),
    path('api/teacher/upload_grades/', views.upload_grades, name='upload_grades'),

    # API Endpoints

    path('api/curriculum/<str:program>/', views.get_curriculum_json, name='get_curriculum_json'),
    path('api/teacher_courses/', views.api_teacher_courses, name='api_teacher_courses'),
    path('api/teacher/classlist/<str:course_code>/<str:section>/', views.get_course_students, name='get_course_students'),
    path('api/teacher/class_grades/<str:course_code>/<str:section>/', views.api_teacher_class_grades, name='TeacherGradesAPI'),

    # Student Management
    path('student/<str:student_id>/status/', views.student_status, name='teacher_student_status'),
    path('teacher/student/<int:student_id>/export/', views.export_student_report, name='export_student_report'),
    path('add_grade/<int:student_id>/<str:course_code>/', views.add_grade, name='add_grade'),
    path("update_student_notes/<int:student_id>/", views.update_student_notes, name="update_student_notes"),

]














  
