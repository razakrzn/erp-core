from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, AttendanceViewSet, EmployeeViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = router.urls
