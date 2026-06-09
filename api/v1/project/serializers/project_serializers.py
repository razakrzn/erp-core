from rest_framework import serializers
from apps.Projects.models import (
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
from api.v1.hrm.serializers import EmployeeLightweightSerializer, DesignationSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserLightSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserLightSerializer(source="assigned_to", read_only=True)

    class Meta:
        model = Task
        fields = "__all__"


class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    employee_detail = EmployeeLightweightSerializer(source="employee", read_only=True)
    designation_detail = DesignationSerializer(source="designation", read_only=True)
    role_display = serializers.CharField(source="get_role_in_project_display", read_only=True)

    class Meta:
        model = ProjectTeamMember
        fields = "__all__"


class ProjectMaterialSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = ProjectMaterial
        fields = "__all__"


class QualityCheckpointSerializer(serializers.ModelSerializer):
    inspected_by_detail = UserLightSerializer(source="inspected_by", read_only=True)

    class Meta:
        model = QualityCheckpoint
        fields = "__all__"


class DeliveryScheduleSerializer(serializers.ModelSerializer):
    driver_detail = UserLightSerializer(source="driver", read_only=True)

    class Meta:
        model = DeliverySchedule
        fields = "__all__"


class ProjectDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_detail = UserLightSerializer(source="uploaded_by", read_only=True)

    class Meta:
        model = ProjectDocument
        fields = "__all__"


class DXFAnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = DXFAnalysisResult
        fields = "__all__"


class DXFFileSerializer(serializers.ModelSerializer):
    analysis_result = DXFAnalysisResultSerializer(read_only=True)
    uploaded_by_detail = UserLightSerializer(source="uploaded_by", read_only=True)

    class Meta:
        model = DXFFile
        fields = "__all__"


class SiteLogPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteLogPhoto
        fields = "__all__"


class SiteLogSerializer(serializers.ModelSerializer):
    photos = SiteLogPhotoSerializer(many=True, read_only=True)
    logged_by_detail = UserLightSerializer(source="logged_by", read_only=True)

    class Meta:
        model = SiteLog
        fields = "__all__"


class TimesheetSerializer(serializers.ModelSerializer):
    employee_detail = UserLightSerializer(source="employee", read_only=True)
    approved_by_detail = UserLightSerializer(source="approved_by", read_only=True)

    class Meta:
        model = Timesheet
        fields = "__all__"


class InstallationLogSerializer(serializers.ModelSerializer):
    team_lead_detail = UserLightSerializer(source="team_lead", read_only=True)

    class Meta:
        model = InstallationLog
        fields = "__all__"


class ReworkRequestSerializer(serializers.ModelSerializer):
    raised_by_detail = UserLightSerializer(source="raised_by", read_only=True)
    assigned_to_detail = UserLightSerializer(source="assigned_to", read_only=True)

    class Meta:
        model = ReworkRequest
        fields = "__all__"


# ─────────────────────────────────────────────────────────────────────────────
# Project Write Serializer
# ─────────────────────────────────────────────────────────────────────────────


class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "project_name",
            "description",
            "location",
            "status",
            "start_date",
            "end_date",
            "actual_end_date",
            "contract_value",
            "quote",
            "boq",
            "client",
            "project_manager",
            "is_active",
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Project List Serializer
# ─────────────────────────────────────────────────────────────────────────────


class ProjectListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.customer_name", read_only=True)
    project_manager_detail = UserLightSerializer(source="project_manager", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "job_number",
            "project_name",
            "description",
            "location",
            "status",
            "status_display",
            "start_date",
            "end_date",
            "actual_end_date",
            "contract_value",
            "client",
            "client_name",
            "project_manager",
            "project_manager_detail",
            "is_active",
            "created_at",
            "updated_at",
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Project Detail Serializer
# ─────────────────────────────────────────────────────────────────────────────


class ProjectDetailSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.customer_name", read_only=True)
    project_manager_detail = UserLightSerializer(source="project_manager", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    # Related lists
    milestones = MilestoneSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    team_members = ProjectTeamMemberSerializer(many=True, read_only=True)
    materials = ProjectMaterialSerializer(source="allocated_materials", many=True, read_only=True)
    quality_checkpoints = QualityCheckpointSerializer(many=True, read_only=True)
    deliveries = DeliveryScheduleSerializer(many=True, read_only=True)
    documents = ProjectDocumentSerializer(many=True, read_only=True)
    site_logs = SiteLogSerializer(many=True, read_only=True)
    dxf_files = DXFFileSerializer(many=True, read_only=True)
    installation_logs = InstallationLogSerializer(many=True, read_only=True)
    rework_requests = ReworkRequestSerializer(many=True, read_only=True)
    timesheets = TimesheetSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "job_number",
            "project_name",
            "description",
            "location",
            "status",
            "status_display",
            "start_date",
            "end_date",
            "actual_end_date",
            "contract_value",
            "client",
            "client_name",
            "project_manager",
            "project_manager_detail",
            "is_active",
            "created_at",
            "updated_at",
            "milestones",
            "tasks",
            "team_members",
            "materials",
            "quality_checkpoints",
            "deliveries",
            "documents",
            "site_logs",
            "dxf_files",
            "installation_logs",
            "rework_requests",
            "timesheets",
        ]
