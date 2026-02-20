from rest_framework import serializers

from apps.hrm.models.designation import Designation


class DesignationSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Designation
        fields = ['id', 'name', 'slug', 'department', 'department_name', 'is_active', 'created_at']
        read_only_fields = ['slug', 'created_at']
