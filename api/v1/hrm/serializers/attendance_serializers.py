from rest_framework import serializers

from apps.hrm.models.attendance import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_name', 'date', 'check_in', 'check_out', 'status', 'created_at']
        read_only_fields = ['created_at']


class CheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['check_in']
        read_only_fields = ['employee', 'date', 'check_out', 'status', 'created_at']


class CheckOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['check_out']
        read_only_fields = ['employee', 'date', 'check_in', 'status', 'created_at']
