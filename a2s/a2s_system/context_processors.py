from .models import StudentProfile

def student_info(request):
    if request.user.is_authenticated and request.user.is_student:
        try:
            profile = request.user.studentprofile
        except StudentProfile.DoesNotExist:
            profile = None
        return {
            'student_user': request.user,
            'student_profile': profile
        }
    return {}
