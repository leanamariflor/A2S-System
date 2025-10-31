from django.urls import path
from . import views

urlpatterns = [
     # Teacher Routes
    path('TeacherDashboard/', views.teacher_dashboard, name='TeacherDashboard'),
    path('TeacherProfile/', views.teacher_profile, name='TeacherProfile'),
    path('UpdateTeacherProfile/', views.update_teacher_profile, name='UpdateTeacherProfile'),
    path('TeacherCourses/', views.teacher_courses, name='TeacherCourses'),
    path('TeacherSchedule/', views.teacher_schedule, name='TeacherSchedule'),



    path('teacher_base/', views.teacher_base, name='teacher_base'),
    path('upload-profile-picture/', views.upload_profile_picture, name='UploadProfilePicture'),
    path("reset-profile-picture/", views.reset_profile_picture, name="reset_profile_picture"),
     
    # API Endpoints
    path('api/curriculum/<str:program>/', views.get_curriculum_json, name='get_curriculum_json'),
    path("api/teacher_courses/", views.api_teacher_courses, name="api_teacher_courses"),
    path('student/<str:student_id>/status/', views.student_status, name='teacher_student_status'),

    path("add_grade/<int:student_id>/<str:course_code>/", views.add_grade, name="add_grade"),

    path('api/teacher_courses/', views.api_teacher_courses, name='api_teacher_courses'),
    path('api/teacher/classlist/<str:course_code>/<str:section>/', views.get_course_students, name='get_course_students'),
    path('TeacherClassList/<str:course_code>/<str:section>/', views.teacher_classlist, name='teacher_classlist'),
    
    path('teacher/student/<int:student_id>/status/', views.student_status, name='student_status'),
    path('teacher/student/<int:student_id>/export/', views.export_student_report, name='export_student_report'),


]










  
