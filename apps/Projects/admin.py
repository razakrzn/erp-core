from django.contrib import admin
from .models import (
    Project,
    ProjectTeamMember,
    Milestone,
    Task,
    SiteLog,
    SiteLogPhoto,
    Timesheet,
    ProjectDocument,
    ProjectMaterial,
    QualityCheckpoint,
    DeliverySchedule,
    ReworkRequest,
    InstallationLog,
    DXFFile,
    DXFAnalysisResult,
)


class ProjectTeamMemberInline(admin.TabularInline):
    model = ProjectTeamMember
    extra = 1


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["job_number", "project_name", "status", "start_date", "end_date", "contract_value", "is_active"]
    list_filter = ["status", "is_active", "created_at"]
    search_fields = ["job_number", "project_name", "description", "location"]
    inlines = [ProjectTeamMemberInline, MilestoneInline, TaskInline]


@admin.register(ProjectTeamMember)
class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ["project", "employee", "designation", "role_in_project", "allocation_pct", "is_active"]
    list_filter = ["role_in_project", "is_active"]
    search_fields = ["project__job_number", "employee__first_name", "employee__last_name"]


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ["project", "name", "status", "due_date", "completion_percentage"]
    list_filter = ["status"]
    search_fields = ["project__job_number", "name"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["project", "title", "assigned_to", "priority", "status", "due_date"]
    list_filter = ["priority", "status"]
    search_fields = ["project__job_number", "title"]


admin.site.register(SiteLog)
admin.site.register(SiteLogPhoto)
admin.site.register(Timesheet)
admin.site.register(ProjectDocument)
admin.site.register(ProjectMaterial)
admin.site.register(QualityCheckpoint)
admin.site.register(DeliverySchedule)
admin.site.register(ReworkRequest)
admin.site.register(InstallationLog)
admin.site.register(DXFFile)
admin.site.register(DXFAnalysisResult)
