from __future__ import annotations

from collections import OrderedDict

from rest_framework import serializers

from apps.company.models import CompanyFeature
from apps.navigation.models import Permission
from apps.rbac.models import Role, RolePermission


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
    """Serializer for Role detail with nested role_permission ids."""

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
        enabled_feature_ids = set(
            CompanyFeature.objects.filter(company_id=obj.company_id, is_enabled=True).values_list("feature_id", flat=True)
        )
        if not enabled_feature_ids:
            return []

        role_permissions = (
            RolePermission.objects.filter(role=obj)
            .select_related("permission__module__feature")
            .order_by(
                "permission__module__feature__order",
                "permission__module__feature__feature_name",
                "permission__module__order",
                "permission__module__module_name",
                "permission__permission_name",
            )
        )

        feature_map: OrderedDict[int, dict] = OrderedDict()

        for role_permission in role_permissions:
            permission = role_permission.permission
            module = permission.module
            feature = module.feature

            if feature.id not in enabled_feature_ids:
                continue

            if feature.id not in feature_map:
                feature_map[feature.id] = {
                    "id": feature.id,
                    "feature_code": feature.feature_code,
                    "feature_name": feature.feature_name,
                    "icon": feature.icon,
                    "order": feature.order,
                    "_modules_map": OrderedDict(),
                }

            modules_map = feature_map[feature.id]["_modules_map"]
            if module.id not in modules_map:
                modules_map[module.id] = {
                    "id": module.id,
                    "feature_name": feature.feature_name,
                    "module_code": module.module_code,
                    "module_name": module.module_name,
                    "route": module.route,
                    "icon": module.icon,
                    "order": module.order,
                    "permissions": [],
                }

            modules_map[module.id]["permissions"].append(
                {
                    "id": permission.id,
                    "module_name": module.module_name,
                    "permission_code": permission.permission_code,
                    "permission_name": permission.permission_name,
                }
            )

        features: list[dict] = []
        for feature_data in feature_map.values():
            modules = list(feature_data.pop("_modules_map").values())
            if not modules:
                continue
            feature_data["modules"] = modules
            features.append(feature_data)

        return features
