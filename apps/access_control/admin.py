from django.contrib import admin
from .models import APIAccessRule


@admin.register(APIAccessRule)
class APIAccessRuleAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "method",
        "path",
        "permission_code",
        "is_active",
    )

    search_fields = ("path", "permission_code")
