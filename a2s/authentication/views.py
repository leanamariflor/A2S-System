from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from supabase import create_client
from datetime import datetime
from datetime import date

import json
import os

from .models import User 


# -----------------------------
# Supabase Setup
# -----------------------------
SUPABASE_URL = "https://qimrryerxdzfewbkoqyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpbXJyeWVyeGR6ZmV3YmtvcXlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4OTkyMjYsImV4cCI6MjA3NDQ3NTIyNn0.RYUzh-HS52HbiMGWhQiGkcf9OY0AeRsm0fuXruw0sEc"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# -----------------------------
# Authentication Views
# -----------------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember = request.POST.get("remember")

        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user_data = response.user

            if not user_data:
                messages.error(request, "Invalid email or password.")
                return redirect("Login")

            if not user_data.email_confirmed_at:
                messages.warning(request, "Please verify your email before logging in.")
                return redirect("Login")

            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                response = redirect("StudentDashboard" if user.is_student else "TeacherDashboard")
                if remember:
                    response.set_cookie("remember_email", email, max_age=30 * 24 * 60 * 60)
                else:
                    response.delete_cookie("remember_email")
                return response

            messages.error(request, "Invalid login credentials.")
            return redirect("Login")

        except Exception as e:
            messages.error(request, f"Login error: {e}")
            return redirect("Login")

    remembered_email = request.COOKIES.get("remember_email", "")
    return render(request, "authentication/Login.html", {"remembered_email": remembered_email})


def register(request):
    if request.method == "POST":
        id_number = request.POST.get("id_number")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        program = request.POST.get("program")
        yearlevel = request.POST.get("yearlevel")
        role = request.POST.get("role")
        agree = request.POST.get("agree")

        # --- Validation ---
        if not all([id_number, first_name, last_name, email, password, password2, role]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("Register")
        if not agree:
            messages.error(request, "You must agree to the Terms of Service.")
            return redirect("Register")
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("Register")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered in the system.")
            return redirect("Register")

        # --- Supabase registration ---
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            if not response.user:
                messages.error(request, "Email already registered or pending verification.")
                return redirect("Register")
        except Exception as e:
            messages.error(request, f"Supabase signup error: {e}")
            return redirect("Register")

        # --- Create local user ---
        is_student = role.lower() == "student"
        is_teacher = role.lower() == "teacher"
        User.objects.create_user(
            id_number=id_number,
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_student=is_student,
            is_teacher=is_teacher,
        )

        messages.success(request, "Account created! Verify your email before logging in.")
        return redirect("Login")

    return render(request, "authentication/Register.html")


def logout_view(request):
    logout(request)
    response = redirect("Login")
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response

def forgot_password(request):
        return render(request, "authentication/ForgotPassword.html")

def reset_password(request):
        return render(request, "authentication/ResetPassword.html")

def landing_page(request):
        return render(request, "authentication/LandingPage.html")

def user_settings(request):
    return render(request, "authentication/Settings.html")