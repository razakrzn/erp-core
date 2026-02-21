from .attendance_views import AttendanceViewSet
from .department_views import DepartmentViewSet, DesignationViewSet
from .employee_views import EmployeeLightweightViewSet, EmployeeViewSet

__all__ = [
    'AttendanceViewSet',
    'DepartmentViewSet',
    'DesignationViewSet',
    'EmployeeLightweightViewSet',
    'EmployeeViewSet',
]
