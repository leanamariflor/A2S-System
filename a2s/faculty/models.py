# faculty/models.py
from django.db import models
from authentication.models import User
from students.models import Achievement


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    achievements = models.ManyToManyField(Achievement, blank=True, related_name='teacher_profiles')

    POSITION_CHOICES = [
        ("Full-Time Faculty", "Full-Time Faculty"),
        ("Part-Time Faculty", "Part-Time Faculty"),
        ("Visiting Lecturer", "Visiting Lecturer"),
        ("Adjunct Faculty", "Adjunct Faculty"),
    ]
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, default="Full-Time Faculty")

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
        return f"{self.user.get_full_name()}"


class TeacherAchievement(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="teacher_achievements")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default="award")

    def __str__(self):
        return f"{self.teacher.user.get_full_name()} - {self.title}"
