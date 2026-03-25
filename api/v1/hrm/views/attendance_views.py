from django.utils import timezone
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action
from core.utils.schema_docs_shims import extend_schema, extend_schema_view, inline_serializer

from apps.hrm.models.attendance import Attendance
from core.utils.responses import APIResponse

from ..serializers.attendance_serializers import AttendanceSerializer


@extend_schema_view(
    list=extend_schema(tags=["HRM-Attendance"], summary="List attendance history"),
    check_in=extend_schema(tags=["HRM-Attendance"], summary="Check-in for today (no payload required)", responses={201: AttendanceSerializer}),
    check_out=extend_schema(tags=["HRM-Attendance"], summary="Check-out for today (no payload required)", responses={200: AttendanceSerializer}),
    report=extend_schema(
        tags=["HRM-Attendance"],
        summary="Get attendance report summary",
        responses={
            200: inline_serializer(
                name="AttendanceReportResponse",
                fields={
                    "total_days": serializers.IntegerField(),
                    "present_days": serializers.IntegerField()
                }
            )
        }
    ),
)
class AttendanceViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing Attendance.
    Supports check-in, check-out, listing history, and report.
    """

    serializer_class = AttendanceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Attendance.objects.select_related('employee', 'employee__user')

        employee = getattr(user, 'employee_profile', None)
        if employee:
            return Attendance.objects.select_related('employee', 'employee__user').filter(employee=employee)

        return Attendance.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Attendance history retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['post'], url_path='check-in')
    def check_in(self, request):
        employee = getattr(request.user, 'employee_profile', None)
        if not employee:
            return APIResponse.error(
                message="Employee profile not found for this user.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        today = timezone.now().date()
        if Attendance.objects.filter(employee=employee, date=today).exists():
            return APIResponse.error(
                message="Already checked in today.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        attendance = Attendance.objects.create(
            employee=employee,
            date=today,
            check_in=timezone.now().time(),
            status='Present',
        )

        serializer = self.get_serializer(attendance)
        return APIResponse.success(
            data=serializer.data,
            message="Checked in successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['post'], url_path='check-out')
    def check_out(self, request):
        employee = getattr(request.user, 'employee_profile', None)
        if not employee:
            return APIResponse.error(
                message="Employee profile not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        today = timezone.now().date()
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return APIResponse.error(
                message="No check-in record found for today.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if attendance.check_out:
            return APIResponse.error(
                message="Already checked out today.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        attendance.check_out = timezone.now().time()
        attendance.save(update_fields=['check_out'])

        serializer = self.get_serializer(attendance)
        return APIResponse.success(
            data=serializer.data,
            message="Checked out successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='report')
    def report(self, request):
        queryset = self.get_queryset()
        total_days = queryset.count()
        present_days = queryset.filter(status='Present').count()

        return APIResponse.success(
            data={
                "total_days": total_days,
                "present_days": present_days,
            },
            message="Attendance report retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
