from django.contrib.auth import get_user_model
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from apps.Projects.models import (
    Project,
    ProjectTeamMember,
)
from core.permissions.rbac_permission import RBACPermission
from core.utils.responses import APIResponse
from ..serializers import (
    ProjectWriteSerializer,
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectTeamMemberSerializer,
)

User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated, RBACPermission]
    permission_prefix = "project.all_projects"

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["client", "is_active", "project_manager", "status"]
    search_fields = ["project_name", "job_number", "description", "location"]
    ordering_fields = ["job_number", "project_name", "start_date", "end_date", "contract_value", "created_at"]
    ordering = ["-created_at"]

    serializer_action_classes = {
        "list": ProjectListSerializer,
        "retrieve": ProjectDetailSerializer,
        "create": ProjectWriteSerializer,
        "update": ProjectWriteSerializer,
        "partial_update": ProjectWriteSerializer,
        "timeline": ProjectWriteSerializer,
        "assign_manager": ProjectWriteSerializer,
        "update_status": ProjectWriteSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, ProjectDetailSerializer)

    def perform_create(self, serializer):
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        serializer.save(
            created_by=user,
            updated_by=user,
        )

    def perform_update(self, serializer):
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        serializer.save(updated_by=user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Projects retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return APIResponse.success(
            data=serializer.data,
            message="Project retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_serializer = ProjectDetailSerializer(serializer.instance, context={"request": request})

        return APIResponse.success(
            data=response_serializer.data,
            message="Project created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_serializer = ProjectDetailSerializer(serializer.instance, context={"request": request})

        return APIResponse.success(
            data=response_serializer.data,
            message="Project updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message="Project deleted successfully.",
            status_code=status.HTTP_200_OK,
        )

    # ─── Custom Action: Edit start/end dates ──────────────────────────────────
    @action(detail=True, methods=["patch"], url_path="timeline")
    def timeline(self, request, *args, **kwargs):
        instance = self.get_object()
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")

        if not start_date and not end_date:
            return APIResponse.error(
                message="At least one of start_date or end_date must be provided.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if start_date:
            instance.start_date = start_date
        if end_date:
            instance.end_date = end_date

        instance.updated_by = request.user if request.user and request.user.is_authenticated else None
        instance.save()

        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message="Project timeline updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    # ─── Custom Action: Assign Project Manager ────────────────────────────────
    @action(detail=True, methods=["patch"], url_path="assign-manager")
    def assign_manager(self, request, *args, **kwargs):
        instance = self.get_object()
        manager_id = request.data.get("project_manager")

        if manager_id is None:
            return APIResponse.error(
                message="project_manager field is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if manager_id == "":
            instance.project_manager = None
        else:
            try:
                manager = User.objects.get(pk=manager_id)
                instance.project_manager = manager
            except User.DoesNotExist:
                return APIResponse.error(
                    message="Manager user not found.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        instance.updated_by = request.user if request.user and request.user.is_authenticated else None
        instance.save()

        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message="Project manager assigned successfully.",
            status_code=status.HTTP_200_OK,
        )

    # ─── Custom Action: Change Project Status ─────────────────────────────────
    @action(detail=True, methods=["patch"], url_path="update-status")
    def update_status(self, request, *args, **kwargs):
        instance = self.get_object()
        new_status = request.data.get("status")

        if not new_status:
            return APIResponse.error(
                message="status field is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        valid_statuses = [choice[0] for choice in Project.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return APIResponse.error(
                message=f"Invalid status value. Choose from: {', '.join(valid_statuses)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        instance.status = new_status
        instance.updated_by = request.user if request.user and request.user.is_authenticated else None
        instance.save()

        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message="Project status updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    # ─── Custom Action: List Active Team Members ──────────────────────────────
    @action(detail=True, methods=["get"], url_path="team")
    def team(self, request, *args, **kwargs):
        instance = self.get_object()
        team_members = instance.team_members.filter(is_active=True)
        serializer = ProjectTeamMemberSerializer(team_members, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Project team retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

