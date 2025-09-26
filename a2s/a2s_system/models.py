# a2s_system/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    id_number = models.CharField(max_length=12, unique=True, null=True, blank=True)


    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username'] 
    REQUIRED_FIELDS = ['id_number'] 

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    program = models.CharField(max_length=100)
    year_level = models.IntegerField()

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
