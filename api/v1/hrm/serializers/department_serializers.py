from rest_framework import serializers

from apps.hrm.models.department import Department
from apps.hrm.models.designation import Designation


class DepartmentDesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'name', 'slug', 'is_active', 'created_at']


class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'slug', 'head_name', 'is_active', 'created_at']
        read_only_fields = ['slug', 'created_at']

    def get_head_name(self, obj):
        return obj.head.full_name if obj.head else None


class DepartmentDetailsSerializer(serializers.ModelSerializer):
    head_details = serializers.SerializerMethodField()
    designations = DepartmentDesignationSerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'slug', 'head_details', 'is_active', 'created_at', 'designations']
        read_only_fields = ['slug', 'created_at']

    def get_head_details(self, obj):
        if not obj.head:
            return None
        return {
            'id': obj.head.id,
            'full_name': obj.head.full_name,
        }
