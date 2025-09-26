from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='Login'),
    path('register/', views.register, name='Register'),
    path('StudentDashboard/', views.student_dashboard, name='StudentDashboard'),
    path('TeacherDashboard/', views.teacher_dashboard, name='TeacherDashboard'),
    path('StudentProfile/', views.student_profile, name='StudentProfile'),
    path('logout/', views.logout_view, name='logout'),
]



