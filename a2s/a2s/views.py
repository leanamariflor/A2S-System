from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages




def login(request):
        # Later: add authentication here
    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')


def student_dashboard(request):
    return render(request, 'StudentDashboard.html')


def student_profile(request):
    # For now, using static data; you can replace with actual user info
    context = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@student.edu",
        "phone": "+1 (555) 123-4567",
        "address": "123 University Ave, Campus City",
        "dob": "May 15, 1999",
        "bio": "Computer Science student passionate about software development and AI.",
        "student_id": "CS-2021-001234",
        "major": "Computer Science",
        "minor": "Mathematics",
        "academic_year": "Senior",
        "expected_grad": "May 2025",
        "gpa": "3.85",
        "credits_completed": "105",
        "credits_max": "120",
    }
    return render(request, "StudentProfile.html", context)
