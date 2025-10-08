from django.urls import path
from . import views


urlpatterns = [
    path('', views.landing_page, name='LandingPage'),
    path('login/', views.login_view, name='Login'),
    path('register/', views.register, name='Register'),
    path('StudentDashboard/', views.student_dashboard, name='StudentDashboard'),
    path('TeacherDashboard/', views.teacher_dashboard, name='TeacherDashboard'),
    path('StudentProfile/', views.student_profile, name='StudentProfile'),
    path('TeacherProfile/', views.teacher_profile, name='TeacherProfile'),
    path('UpdateStudentProfile/', views.update_student_profile, name='UpdateStudentProfile'),


    path('Logout/', views.logout_view, name='Logout'),
    path('ForgotPassword/', views.forgot_password, name='ForgotPassword'),
    path('ResetPassword/', views.reset_password, name='ResetPassword'),
    path('settings/', views.user_settings, name='settings'),
    path('student_base/', views.student_base, name='student_base'),
    path('teacher_base/', views.teacher_base, name='teacher_base'),
    path('student_base/', views.student_base, name='student_base'),
    path('StudentSchedule/', views.student_schedule, name='StudentSchedule'),
    path('StudentCourses/', views.student_courses, name='StudentCourses'),
    path('StudentGrades/', views.student_grades, name='StudentGrades'),
    path('StudentCurriculum/', views.student_curriculum, name='StudentCurriculum'),
    path('api/curriculum/<str:program>/', views.get_curriculum_json, name='get_curriculum_json'),

   

]



