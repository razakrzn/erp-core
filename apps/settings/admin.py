from django.contrib import admin
from .models import GlobalTerms

@admin.register(GlobalTerms)
class GlobalTermsAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_default", "is_approved", "created_at", "updated_at")
    search_fields = ("title", "category", "content")
    list_filter = ("category", "is_default", "is_approved")
