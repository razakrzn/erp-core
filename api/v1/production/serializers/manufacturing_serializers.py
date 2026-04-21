from rest_framework import serializers

from apps.production.models import (
    BOMExplosion,
    BatchTracking,
    LaborTracking,
    MachineIntegration,
    ProductionOrder,
    ProductionPlanning,
    RejectionReworkManagement,
    ShopFloorControl,
    SubcontractingManagement,
    WIPTracking,
)


class ProductionPlanningSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionPlanning
        fields = "__all__"
        read_only_fields = ["slug", "created_at", "updated_at"]


class ProductionOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionOrder
        fields = "__all__"
        read_only_fields = ["slug", "created_at", "updated_at"]


class ShopFloorControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopFloorControl
        fields = "__all__"
        read_only_fields = ["slug", "created_at", "updated_at"]


class BOMExplosionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BOMExplosion
        fields = "__all__"
        read_only_fields = ["slug", "created_at", "updated_at"]


class MachineIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineIntegration
        fields = "__all__"
        read_only_fields = ["slug", "created_at", "updated_at"]


class LaborTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaborTracking
        fields = "__all__"
        read_only_fields = ["slug", "created_at", "updated_at"]


class WIPTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WIPTracking
        fields = "__all__"
        read_only_fields = ["slug", "created_at", "updated_at"]


class SubcontractingManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubcontractingManagement
        fields = "__all__"
        read_only_fields = ["slug", "created_at", "updated_at"]


class BatchTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchTracking
        fields = "__all__"
        read_only_fields = ["slug", "created_at", "updated_at"]


class RejectionReworkManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RejectionReworkManagement
        fields = "__all__"
        read_only_fields = ["slug", "created_at", "updated_at"]
