from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html

from apps.assessment.models import QuoteItem
from apps.inventory.models import Product

from .models import (
    Project,
    ProjectTeamMember,
)


class ProjectTeamMemberInline(admin.TabularInline):
    model = ProjectTeamMember
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["job_number", "project_name", "status", "start_date", "end_date", "contract_value", "is_active"]
    list_filter = ["status", "is_active", "created_at"]
    search_fields = ["job_number", "project_name", "description", "location"]
    inlines = [ProjectTeamMemberInline]


@admin.register(ProjectTeamMember)
class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ["project", "employee", "designation", "role_in_project", "allocation_pct", "is_active"]
    list_filter = ["role_in_project", "is_active"]
    search_fields = ["project__job_number", "employee__first_name", "employee__last_name"]



