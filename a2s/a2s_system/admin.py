from django.contrib import admin
from .models import Curriculum

@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ("program",)
    search_fields = ("program",)
