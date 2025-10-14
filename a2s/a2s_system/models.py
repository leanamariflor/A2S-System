# a2s_system/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField  # or models.JSONField in Django 3.1+


class Curriculum(models.Model):
    program = models.CharField(max_length=50)  # e.g., BSIT, BSCS, etc.
    data = models.JSONField()  # stores the actual curriculum content (from your JSON file)

    def __str__(self):
        return self.program


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    id_number = models.CharField(max_length=12, unique=True, null=True, blank=True)


    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username', 'id_number']
    

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    program = models.CharField(max_length=100, default='Undeclared')
    year_level = models.IntegerField(default=1)
    
    # New fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Academic progress
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    credits_completed = models.IntegerField(blank=True, null=True)
    credits_required = models.IntegerField(blank=True, null=True)
    academic_standing = models.CharField(max_length=50, default="Good Standing")
    expected_graduation = models.DateField(blank=True, null=True)



class TeacherAchievement(models.Model):
    teacher = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.CASCADE,
        related_name="teacher_achievements"  # <-- changed to avoid clash
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default="award")

    def __str__(self):
        return f"{self.teacher.user.get_full_name()} - {self.title}"



class Course(models.Model):
    course_name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.course_name

class Grade(models.Model):
    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, related_name='grades')

    # Keep original relation but add readable fields for Supabase import
    course = models.ForeignKey('Course', on_delete=models.CASCADE, blank=True, null=True)

    # Redundant fields for Supabase import and quick access
    course_code = models.CharField(max_length=50, blank=True, null=True)
    course_name = models.CharField(max_length=100, blank=True, null=True)


    faculty = models.CharField(max_length=100, blank=True, null=True)
    units = models.IntegerField(default=3)

    # Detailed grading fields
    midterm = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    final = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    final_grade = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)  # e.g. "PASSED", "FAILED"

    # Academic term info
    school_year = models.CharField(max_length=9, default="2324")  # e.g., "2324"
    semester = models.CharField(max_length=20, default="First")   # e.g., "First", "Second"

    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course_code} ({self.final_grade})"



class Achievement(models.Model):
    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, related_name="achievements")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default="award")  # icon for lucide

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.title}"
    
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    
    achievements = models.ManyToManyField('Achievement', blank=True, related_name='teacher_profiles')

    # Position choices
    POSITION_CHOICES = [
        ("Full-Time Faculty", "Full-Time Faculty"),
        ("Part-Time Faculty", "Part-Time Faculty"),
        ("Visiting Lecturer", "Visiting Lecturer"),
        ("Adjunct Faculty", "Adjunct Faculty"),
    ]
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, default="Full-Time Faculty")

    # Department/College choices (CIT University)
    DEPARTMENT_CHOICES = [
        ("CEA", "Engineering and Architecture"),
        ("CCS", "Computer Studies"),
        ("CASE", "Arts, Sciences and Education"),
        ("CMBA", "Management, Business and Accountancy"),
        ("CNAHS", "Nursing and Allied Health Sciences"),
        ("CCJ", "Criminal Justice"),
    ]
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} Profile"


@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.is_student:
        StudentProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    if instance.is_student:
        instance.studentprofile.save()

@receiver(post_save, sender=User)
def create_teacher_profile(sender, instance, created, **kwargs):
    if created and instance.is_teacher:
        TeacherProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_teacher_profile(sender, instance, **kwargs):
    if instance.is_teacher:
        instance.teacherprofile.save()



class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    schedule_day = models.CharField(max_length=10, choices=[
        ('Mon','Monday'), ('Tue','Tuesday'), ('Wed','Wednesday'),
        ('Thu','Thursday'), ('Fri','Friday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course.course_name}"
