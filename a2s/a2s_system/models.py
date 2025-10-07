# a2s_system/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)

class Course(models.Model):
    course_name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.course_name


class Grade(models.Model):
    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    grade = models.CharField(max_length=10, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.course} ({self.grade})"


class Achievement(models.Model):
    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, related_name="achievements")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default="award")  # icon for lucide

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.title}"

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.is_student:
        StudentProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    if instance.is_student:
        instance.studentprofile.save()