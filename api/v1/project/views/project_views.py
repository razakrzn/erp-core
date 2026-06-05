from django.contrib.auth import get_user_model
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from apps.Projects.models import (
    Project,
    ProjectTeamMember,
    Milestone,
    Task,
    DXFFile,
    DXFAnalysisResult,
)
from core.permissions.rbac_permission import RBACPermission
from core.utils.responses import APIResponse
from ..serializers import (
    ProjectWriteSerializer,
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectTeamMemberSerializer,
    DXFFileSerializer,
)

User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated, RBACPermission]
    permission_prefix = "projects.projects"
    
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
        return self.serializer_action_classes.get(
            self.action,
            ProjectDetailSerializer
        )

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

        response_serializer = ProjectDetailSerializer(
            serializer.instance,
            context={"request": request}
        )

        return APIResponse.success(
            data=response_serializer.data,
            message="Project created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_serializer = ProjectDetailSerializer(
            serializer.instance,
            context={"request": request}
        )

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

    # ─── Custom Action: Summary Card ──────────────────────────────────────────
    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, *args, **kwargs):
        instance = self.get_object()
        
        milestones = instance.milestones.all()
        total_milestones = milestones.count()
        completed_milestones = milestones.filter(status="completed").count()
        milestone_progress = round((completed_milestones / total_milestones * 100), 2) if total_milestones > 0 else 0.0

        tasks = instance.tasks.all()
        total_tasks = tasks.count()
        task_stats = {
            "todo": tasks.filter(status="todo").count(),
            "in_progress": tasks.filter(status="in_progress").count(),
            "review": tasks.filter(status="review").count(),
            "done": tasks.filter(status="done").count(),
            "blocked": tasks.filter(status="blocked").count(),
        }

        team_count = instance.team_members.count()

        materials = instance.materials.all()
        material_count = materials.count()
        estimated_cost = float(sum(m.total_cost for m in materials))
        issued_materials = materials.filter(status="issued").count()

        qas = instance.quality_checkpoints.all()
        qa_stats = {
            "total": qas.count(),
            "pending": qas.filter(result="pending").count(),
            "pass": qas.filter(result="pass").count(),
            "fail": qas.filter(result="fail").count(),
        }

        reworks = instance.rework_requests.all()
        rework_stats = {
            "total": reworks.count(),
            "open": reworks.filter(status="open").count(),
            "resolved": reworks.filter(status="resolved").count(),
        }

        data = {
            "project_name": instance.project_name,
            "job_number": instance.job_number,
            "status": instance.status,
            "contract_value": float(instance.contract_value),
            "milestones": {
                "total": total_milestones,
                "completed": completed_milestones,
                "completion_percentage": milestone_progress,
            },
            "tasks": {
                "total": total_tasks,
                **task_stats
            },
            "team_members_count": team_count,
            "materials": {
                "total_items": material_count,
                "total_estimated_cost": estimated_cost,
                "total_issued": issued_materials,
            },
            "quality_checkpoints": qa_stats,
            "rework_requests": rework_stats,
        }
        return APIResponse.success(
            data=data,
            message="Project summary retrieved successfully.",
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

    # ─── Custom Action: Upload and Analyze DXF ────────────────────────────────
    @action(detail=True, methods=["post"], url_path="dxf/upload")
    def dxf_upload(self, request, *args, **kwargs):
        instance = self.get_object()
        dxf_file_obj = request.FILES.get("file")
        
        if not dxf_file_obj:
            return APIResponse.error(
                message="No file uploaded. Please upload a .dxf file.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            
        if not dxf_file_obj.name.lower().endswith(".dxf"):
            return APIResponse.error(
                message="Unsupported file format. Only .dxf files are supported.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            
        # Create the DXFFile registry record
        dxf_record = DXFFile.objects.create(
            project=instance,
            file=dxf_file_obj,
            status="processing",
            uploaded_by=request.user if request.user and request.user.is_authenticated else None,
        )
        
        # Run optimization
        from apps.production.services.cutting_optimization import run_cutting_optimization
        try:
            optimization_result = run_cutting_optimization(dxf_record.file.path)
            summary = optimization_result.get("summary", {})
            
            # Save analysis results
            DXFAnalysisResult.objects.create(
                dxf_file=dxf_record,
                total_parts=summary.get("total_parts", 0),
                placed_parts=summary.get("placed_parts", 0),
                unplaced_parts=summary.get("unplaced_parts", 0),
                oversized_parts=summary.get("oversized_parts", 0),
                utilization_percent=summary.get("utilization_percent", 0.0),
                raw_data=optimization_result,
            )
            
            dxf_record.status = "completed"
            dxf_record.save()
        except Exception as e:
            dxf_record.status = "failed"
            dxf_record.save()
            return APIResponse.error(
                message=f"DXF analysis optimization failed: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
        # Serialize the updated DXF record
        serializer = DXFFileSerializer(dxf_record)
        return APIResponse.success(
            data=serializer.data,
            message="DXF file uploaded and analyzed successfully using cutting optimization.",
            status_code=status.HTTP_200_OK,
        )

    # ─── Custom Action: Gantt-ready milestone+task data ────────────────────────
    @action(detail=True, methods=["get"], url_path="gantt")
    def gantt(self, request, *args, **kwargs):
        instance = self.get_object()
        milestones = instance.milestones.all().order_by("order", "created_at")
        
        gantt_data = []
        for milestone in milestones:
            gantt_data.append({
                "id": f"milestone-{milestone.id}",
                "name": milestone.name,
                "start_date": milestone.start_date.isoformat() if milestone.start_date else None,
                "end_date": milestone.due_date.isoformat() if milestone.due_date else None,
                "status": milestone.status,
                "progress": milestone.completion_percentage,
                "type": "project",
                "dependencies": []
            })
            
            tasks = milestone.tasks.all().order_by("created_at")
            for task in tasks:
                gantt_data.append({
                    "id": f"task-{task.id}",
                    "name": task.title,
                    "start_date": task.start_date.isoformat() if task.start_date else None,
                    "end_date": task.due_date.isoformat() if task.due_date else None,
                    "status": task.status,
                    "progress": task.completion_percentage,
                    "type": "task",
                    "parent": f"milestone-{milestone.id}",
                    "dependencies": []
                })
                
        return APIResponse.success(
            data=gantt_data,
            message="Gantt-ready project milestones and tasks retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
