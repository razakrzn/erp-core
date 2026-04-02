from __future__ import annotations

from django.db import IntegrityError
from rest_framework import status

from core.utils.responses import APIResponse

from apps.rbac.models import Role

from ..serializers import RoleDetailSerializer, RoleSerializer, RoleWriteSerializer
from .shared import BaseRBACViewSet, _get_company_id


class RoleViewSet(BaseRBACViewSet):
    queryset = Role.objects.select_related("company").prefetch_related("role_permissions__permission").order_by(
        "company", "role_name"
    )
    serializer_class = RoleSerializer
    permission_prefix = ["core.roles", "hr.roles"]

    def get_queryset(self):
        queryset = super().get_queryset()

        company_id = _get_company_id(self.request, self.kwargs)
        if company_id is not None:
            queryset = queryset.filter(company_id=company_id)

        requested_company_id = self.request.query_params.get("company_id")
        if requested_company_id is not None:
            queryset = queryset.filter(company_id=requested_company_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RoleDetailSerializer
        if self.action in ["create", "update", "partial_update"]:
            return RoleWriteSerializer
        return RoleSerializer

    def create(self, request, *args, **kwargs):
        company_id = _get_company_id(request, self.kwargs)

        if request.user.is_superuser:
            override_company_id = request.data.get("company_id")
            if override_company_id is not None:
                try:
                    company_id = int(override_company_id)
                except (ValueError, TypeError):
                    return APIResponse.error(
                        message="Invalid company_id.",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

        if company_id is None:
            return APIResponse.error(
                message="Company context is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RoleWriteSerializer(
            data=request.data,
            context={"company_id": company_id},
        )
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            instance = serializer.save()
        except IntegrityError as e:
            if "uniq_rbac_role_company_code" in str(e):
                return APIResponse.error(
                    message="A role with this code already exists for your company.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            raise

        read_serializer = RoleDetailSerializer(instance, context={"request": request})
        return APIResponse.success(
            data=read_serializer.data,
            message="Role created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = RoleWriteSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={"company_id": instance.company_id},
        )
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        updated = serializer.save()
        return APIResponse.success(
            data=RoleSerializer(updated).data,
            message="Role updated successfully.",
            status_code=status.HTTP_200_OK,
        )
