from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.landing_page, name='LandingPage'),
    path('login/', views.login_view, name='Login'),
    path('register/', views.register, name='Register'),
    path('ForgotPassword/', views.forgot_password, name='ForgotPassword'),
    path('ResetPassword/', views.reset_password, name='ResetPassword'),

    # Logout & Settings
    path('Logout/', views.logout_view, name='Logout'),
    path('settings/', views.user_settings, name='settings'),

   
]
