# students/models.py
from django.db import models
from authentication.models import User


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    program = models.CharField(max_length=100, default='Undeclared')
    year_level = models.IntegerField(default=1)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    credits_completed = models.IntegerField(blank=True, null=True)
    credits_required = models.IntegerField(blank=True, null=True)
    academic_standing = models.CharField(max_length=50, default="Good Standing")
    expected_graduation = models.DateField(blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)


    def __str__(self):
        return f"{self.user.get_full_name()}"


class Achievement(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="achievements")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default="award")

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.title}"


class Course(models.Model):
    course_name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.course_name


class Grade(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    course_code = models.CharField(max_length=50, blank=True, null=True)
    course_name = models.CharField(max_length=100, blank=True, null=True)
    faculty = models.CharField(max_length=100, blank=True, null=True)
    units = models.IntegerField(default=3)
    midterm = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    final = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    final_grade = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    school_year = models.CharField(max_length=9, default="2324")
    semester = models.CharField(max_length=20, default="First")
    remarks = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True)  
    teacher = models.ForeignKey('teacher.TeacherProfile', on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course_code}"


class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    schedule_day = models.CharField(max_length=10, choices=[
        ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'), ('Fri', 'Friday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course.course_name}"


class Curriculum(models.Model):
    program = models.CharField(max_length=50)
    data = models.JSONField()

    class Meta:
        db_table = 'a2s_system_curriculum'

    def __str__(self):
        return self.program


class Schedule(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='schedules')
    code = models.CharField(max_length=20)
    section = models.CharField(max_length=20)
    room = models.CharField(max_length=100)
    day = models.CharField(max_length=20, default="TBA")
    time_start = models.TimeField(default="00:00")
    time_end = models.TimeField(default="00:00")


    def __str__(self):
        return f"{self.student.user.username} - {self.code} ({self.section})"



class CourseAssignment(models.Model):
    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, related_name='course_assignments')
    teacher = models.ForeignKey('teacher.TeacherProfile', on_delete=models.CASCADE, related_name='student_assignments')
    course_code = models.CharField(max_length=50)
    section = models.CharField(max_length=50, default="G1") 

    class Meta:
        unique_together = ('student', 'teacher', 'course_code', 'section')

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course_code} {self.section} ({self.teacher.user.get_full_name()})"


class Notification(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True) 
    date_created = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.title}"
