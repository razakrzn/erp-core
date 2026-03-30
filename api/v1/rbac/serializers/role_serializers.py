from rest_framework import serializers
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

    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "role_name",
            "role_code",
            "description",
            "is_active",
            "created_at",
            "permissions",
        ]

    def get_permissions(self, obj: Role) -> list[dict]:
        return [
            {
                "id": rp.permission_id,
                "permission_name": rp.permission.permission_name,
                "permission_code": rp.permission.permission_code,
            }
            for rp in obj.role_permissions.select_related("permission").all()
        ]
