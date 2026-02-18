from django.contrib import admin
from apps.hrm.models.department import Department
from apps.hrm.models.employee import Employee
from apps.hrm.models.designation import Designation
from apps.hrm.models.attendance import Attendance

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head')
    search_fields = ('name', 'code')
    list_filter = ('head',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ('first_name', 'last_name')
    list_filter = ('department', 'designation')

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'head')
    search_fields = ('name', 'code')
    list_filter = ('department', 'head')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status')
    search_fields = ('employee__first_name', 'employee__last_name')
    list_filter = ('date', 'status')
