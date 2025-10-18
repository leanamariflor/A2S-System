from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.landing_page, name='LandingPage'),
   
]
