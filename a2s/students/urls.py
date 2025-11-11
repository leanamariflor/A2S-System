
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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

    # Export Routes
    path('export-degree-audit-pdf/', views.export_degree_audit_pdf, name='ExportDegreeAuditPDF'),
    path('export-degree-audit-excel/', views.export_degree_audit_excel, name='ExportDegreeAuditExcel'),

    path('upload-profile-picture/', views.upload_student_profile_picture, name='UploadProfilePicture'),
    path("reset-profile-picture/", views.reset_student_profile_picture, name="reset_profile_picture"),

    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/read/', views.mark_notification_read, name='mark_notification_read'),

    # Base Templates
   path('student_base/', views.student_base, name='student_base'),
   path('api/curriculum/<str:program>/', views.get_curriculum_json, name='get_curriculum_json'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)