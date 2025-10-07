from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from a2s_system.models import StudentProfile

@login_required
def student_dashboard(request):
    
    student_profile = None
    if hasattr(request.user, 'studentprofile'):
        student_profile = request.user.studentprofile

    return render(request, "dashboard.html", {
        "user": request.user,
        "student_profile": student_profile
    })
