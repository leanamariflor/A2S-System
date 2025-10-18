# authentication/models.py
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


@receiver(post_save, sender=User)
def create_profiles(sender, instance, created, **kwargs):
    """Automatically create related profiles based on role."""
    from students.models import StudentProfile
    from faculty.models import TeacherProfile

    if created:
        if instance.is_student:
            StudentProfile.objects.create(user=instance)
        elif instance.is_teacher:
            TeacherProfile.objects.create(user=instance)
