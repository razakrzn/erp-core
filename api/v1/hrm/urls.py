from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, DesignationViewSet, AttendanceViewSet, EmployeeViewSet, EmployeeLightweightViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'designations', DesignationViewSet, basename='designation')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'employees-lightweight', EmployeeLightweightViewSet, basename='employee-lightweight')

urlpatterns = router.urls
