from django.contrib import admin
from .models import TermsConditions


@admin.register(TermsConditions)
class TermsConditionsAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_default")
    search_fields = ("title", "category", "content")
    list_filter = ("category", "is_default")
