from django.urls import path
from . import views

urlpatterns = [
     # Teacher Routes
    path('TeacherDashboard/', views.teacher_dashboard, name='TeacherDashboard'),
    path('TeacherProfile/', views.teacher_profile, name='TeacherProfile'),
    path('UpdateTeacherProfile/', views.update_teacher_profile, name='UpdateTeacherProfile'),
    path('TeacherCourses/', views.teacher_courses, name='TeacherCourses'),

    path('teacher_base/', views.teacher_base, name='teacher_base'),

     
    # API Endpoints
    path('api/curriculum/<str:program>/', views.get_curriculum_json, name='get_curriculum_json'),
    path("api/teacher_courses/", views.api_teacher_courses, name="api_teacher_courses"),
]







  
