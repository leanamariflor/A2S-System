
from django.urls import path
from . import views

urlpatterns = [
   # Student Routes
    path('StudentDashboard/', views.student_dashboard, name='StudentDashboard'),
    path('StudentProfile/', views.student_profile, name='StudentProfile'),
    path('UpdateStudentProfile/', views.update_student_profile, name='UpdateStudentProfile'),
    path('StudentSchedule/', views.student_schedule, name='StudentSchedule'),
    path('StudentCourses/', views.student_courses, name='StudentCourses'),
    path('StudentGrades/', views.student_grades, name='StudentGrades'),
    path('StudentCurriculum/', views.student_curriculum, name='StudentCurriculum'),
    path('StudentDegreeAudit/', views.student_degree_audit, name='StudentDegreeAudit'),

   

    # Base Templates
    path('student_base/', views.student_base, name='student_base'),
   path('api/curriculum/<str:program>/', views.get_curriculum_json, name='get_curriculum_json'),

]


