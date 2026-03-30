from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from core.permissions.rbac_permission import RBACPermission


from core.utils.responses import APIResponse, build_actions


class BaseAssessmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_ordering(self):
        """
        Default to '-created_at' if it exists, otherwise fallback to '-id'.
        """
        ordering = getattr(self, "ordering", ["-created_at"])
        if isinstance(ordering, (list, tuple)):
            clean_ordering = [o for o in ordering if self._model_has_field(o.lstrip("-"))]
            return clean_ordering if clean_ordering else ["-id"]
        return ordering

    def _model_has_field(self, field_name):
        return field_name in {field.name for field in self.get_queryset().model._meta.fields}

    def perform_create(self, serializer):
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        save_kwargs = {}
        if user and self._model_has_field("created_by"):
            save_kwargs["created_by"] = user
        if user and self._model_has_field("updated_by"):
            save_kwargs["updated_by"] = user
        serializer.save(**save_kwargs)

    def perform_update(self, serializer):
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        save_kwargs = {}
        if user and self._model_has_field("updated_by"):
            save_kwargs["updated_by"] = user
        serializer.save(**save_kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.queryset.model._meta.verbose_name_plural.title()} retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        prefix = getattr(self, "permission_prefix", None)
        data = serializer.data

        # Detail API: expose only approve/reject actions (including explicit false values).
        if prefix:
            computed_actions = build_actions(request.user, prefix)
            detail_actions = {}
            if "canApprove" in computed_actions:
                detail_actions["canApprove"] = bool(computed_actions.get("canApprove"))
            if "canReject" in computed_actions:
                detail_actions["canReject"] = bool(computed_actions.get("canReject"))
            if detail_actions and isinstance(data, dict):
                data = {**data, "actions": detail_actions}

        return APIResponse.success(
            data=data,
            message=f"{self.queryset.model._meta.verbose_name.title()} retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.queryset.model._meta.verbose_name.title()} created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.queryset.model._meta.verbose_name.title()} updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message=f"{self.queryset.model._meta.verbose_name.title()} deleted successfully.",
            status_code=status.HTTP_200_OK,
        )
