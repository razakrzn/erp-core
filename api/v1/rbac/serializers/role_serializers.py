from __future__ import annotations

from rest_framework import serializers
from django.db.models import Prefetch

from apps.company.models import CompanyFeature
from apps.navigation.models import Feature, Module, Permission
from apps.rbac.models import Role, RolePermission

SUPERUSER_ONLY_FEATURE_CODES = {"superuser", "core"}


def _is_superuser_only_feature(feature_code: str | None) -> bool:
    return (feature_code or "").lower() in SUPERUSER_ONLY_FEATURE_CODES


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role (read, with nested role_permissions)."""

    class Meta:
        model = Role
        fields = [
            "id",
            "role_name",
            "role_code",
            "description",
            "is_active",
            "created_at",
        ]


class RoleWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Role (optional permissions on create and PUT/PATCH)."""

    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False,
        write_only=True,
        help_text="Optional list of permission IDs to assign on create or replace on update (PUT/PATCH).",
    )

    class Meta:
        model = Role
        fields = ["role_name", "role_code", "description", "is_active", "permissions"]

    def validate_role_code(self, value: str) -> str:
        company_id = self.context.get("company_id")
        if company_id is None:
            return value
        qs = Role.objects.filter(company_id=company_id, role_code=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A role with this code already exists for your company.")
        return value

    def create(self, validated_data: dict) -> Role:
        validated_data["company_id"] = self.context["company_id"]
        permission_list = validated_data.pop("permissions", [])
        instance = super().create(validated_data)
        if permission_list:
            RolePermission.objects.bulk_create(
                [RolePermission(role=instance, permission=p) for p in permission_list],
                ignore_conflicts=True,
            )
        return instance

    def update(self, instance: Role, validated_data: dict) -> Role:
        permission_list = validated_data.pop("permissions", None)
        instance = super().update(instance, validated_data)
        if permission_list is not None:
            RolePermission.objects.filter(role=instance).delete()
            if permission_list:
                RolePermission.objects.bulk_create(
                    [RolePermission(role=instance, permission=p) for p in permission_list],
                    ignore_conflicts=True,
                )
        return instance


class RoleDetailSerializer(serializers.ModelSerializer):
    """Serializer for Role detail with full company navigation and enabled permissions."""

    features = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "role_name",
            "role_code",
            "description",
            "is_active",
            "created_at",
            "features",
        ]

    def get_features(self, obj: Role) -> list[dict]:
        request = self.context.get("request")
        is_superuser = bool(getattr(getattr(request, "user", None), "is_superuser", False))

        enabled_feature_ids = set(
            CompanyFeature.objects.filter(company_id=obj.company_id, is_enabled=True).values_list("feature_id", flat=True)
        )
        if not enabled_feature_ids:
            return []

        assigned_permission_ids = set(
            RolePermission.objects.filter(role=obj).values_list("permission_id", flat=True)
        )

        feature_qs = (
            Feature.objects.filter(id__in=enabled_feature_ids)
            .prefetch_related(
                Prefetch(
                    "modules",
                    queryset=Module.objects.prefetch_related(
                        Prefetch("permissions", queryset=Permission.objects.all().order_by("permission_name", "id"))
                    ).order_by("order", "module_name", "id"),
                )
            )
            .order_by("order", "feature_name", "id")
        )

        features: list[dict] = []
        for feature in feature_qs:
            if _is_superuser_only_feature(feature.feature_code) and not is_superuser:
                continue

            modules: list[dict] = []
            for module in feature.modules.all():
                permissions = [
                    {
                        "id": permission.id,
                        "permission_name": permission.permission_name,
                        "enabled": permission.id in assigned_permission_ids,
                    }
                    for permission in module.permissions.all()
                ]

                modules.append(
                    {
                        "id": module.id,
                        "module_name": module.module_name,
                        "icon": module.icon,
                        "order": module.order,
                        "permissions": permissions,
                    }
                )

            features.append(
                {
                    "id": feature.id,
                    "feature_name": feature.feature_name,
                    "icon": feature.icon,
                    "order": feature.order,
                    "modules": modules,
                }
            )

        return features
