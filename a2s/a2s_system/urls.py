from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.landing_page, name='LandingPage'),
    path('login/', views.login_view, name='Login'),
    path('register/', views.register, name='Register'),
    path('ForgotPassword/', views.forgot_password, name='ForgotPassword'),
    path('ResetPassword/', views.reset_password, name='ResetPassword'),

    # Logout & Settings
    path('Logout/', views.logout_view, name='Logout'),
    path('settings/', views.user_settings, name='settings'),

    # Student Routes
    path('StudentDashboard/', views.student_dashboard, name='StudentDashboard'),
    path('StudentProfile/', views.student_profile, name='StudentProfile'),
    path('UpdateStudentProfile/', views.update_student_profile, name='UpdateStudentProfile'),
    path('StudentSchedule/', views.student_schedule, name='StudentSchedule'),
    path('StudentCourses/', views.student_courses, name='StudentCourses'),
    path('StudentGrades/', views.student_grades, name='StudentGrades'),
    path('StudentCurriculum/', views.student_curriculum, name='StudentCurriculum'),

    # Teacher Routes
    path('TeacherDashboard/', views.teacher_dashboard, name='TeacherDashboard'),
    path('TeacherProfile/', views.teacher_profile, name='TeacherProfile'),
    path('UpdateTeacherProfile/', views.update_teacher_profile, name='UpdateTeacherProfile'),
    path('TeacherCourses/', views.teacher_courses, name='TeacherCourses'),


    # Base Templates
    path('student_base/', views.student_base, name='student_base'),
    path('teacher_base/', views.teacher_base, name='teacher_base'),

    # API Endpoints
    path('api/curriculum/<str:program>/', views.get_curriculum_json, name='get_curriculum_json'),
      path("api/teacher_courses/", views.api_teacher_courses, name="api_teacher_courses"),
]
