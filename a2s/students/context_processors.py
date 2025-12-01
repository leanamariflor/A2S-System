from students.models import StudentProfile

def student_info(request):
    if request.user.is_authenticated and request.user.is_student:
        try:
            profile = request.user.studentprofile
        except StudentProfile.DoesNotExist:
            profile = None
        # Provide common student attributes to templates so pages remain consistent
        year_level = None
        program = None
        if profile:
            year_level = getattr(profile, 'year_level', None)
            program = getattr(profile, 'program', None)
        return {
            'student_user': request.user,
            'student_profile': profile,
            'year_level': year_level,
            'student_program': program,
        }
    return {}
