from rest_framework import serializers
from apps.Projects.models import (
    Project,
    ProjectTeamMember,
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


class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    employee_detail = EmployeeLightweightSerializer(source="employee", read_only=True)
    designation_detail = DesignationSerializer(source="designation", read_only=True)
    role_display = serializers.CharField(source="get_role_in_project_display", read_only=True)

    class Meta:
        model = ProjectTeamMember
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
    team_members = ProjectTeamMemberSerializer(many=True, read_only=True)

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
            "team_members",
        ]
