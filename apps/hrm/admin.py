from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.hrm.models.department import Department
from apps.hrm.models.employee import Employee
from apps.hrm.models.designation import Designation
from apps.hrm.models.attendance import Attendance
from apps.hrm.models.leave import LeaveType, LeaveRequest
from apps.rbac.models import Role, UserRole

User = get_user_model()

class EmployeeAdminForm(forms.ModelForm):
    create_user = forms.BooleanField(required=False, label="Create User Account", initial=False, help_text="Check this to create a login account for this employee.")
    username = forms.CharField(required=False, help_text="Required if creating a user account.")
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Required if creating a user account.")
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False, help_text="Select a role if creating a user account.", empty_label="---------")

    class Meta:
        model = Employee
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.user:
            self.initial['first_name'] = self.instance.user.first_name
            self.instance.first_name = self.instance.user.first_name # for display in form field value
            self.initial['last_name'] = self.instance.user.last_name
            self.instance.last_name = self.instance.user.last_name
            self.initial['email'] = self.instance.user.email
            self.instance.email = self.instance.user.email
            self.initial['username'] = self.instance.user.username
            
            # Populate Role
            user_role = UserRole.objects.filter(user=self.instance.user).first()
            if user_role:
                self.initial['role'] = user_role.role

    def clean(self):
        cleaned_data = super().clean()
        create_user = cleaned_data.get('create_user')
        user = cleaned_data.get('user')

        if create_user:
            if user:
                 raise ValidationError("You cannot create a new user if an existing user is already selected.")
            if not cleaned_data.get('username') or not cleaned_data.get('password'):
                raise ValidationError("Username and Password are required when creating a new user account.")
            
            if not cleaned_data.get('email'):
                raise ValidationError("Email is required when creating a new user account.")
            
            if not cleaned_data.get('role'):
                raise ValidationError("Role is required when creating a new user account.")

            # check if username already exists
            username = cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                 raise ValidationError(f"User with username '{username}' already exists.")
            
            # check if email already exists
            email = cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                 raise ValidationError(f"User with email '{email}' already exists.")

        return cleaned_data

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'head')
    search_fields = ('name', 'slug')
    list_filter = ('head',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeAdminForm
    list_display = ('full_name', 'get_email', 'department', 'designation', 'company', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'company__name')
    list_filter = ('company', 'department', 'designation', 'is_active')
    
    fieldsets = (
        ('Employee Details', {
            'fields': ('department', 'designation', 'is_active')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email'),
            'description': 'Enter name and email here. If a user is created or linked, these will be synced/moved to the User record.'
        }),
        ('User Account', {
            'fields': ('user', 'create_user', 'username', 'password', 'role'),
            'description': 'Link an existing user OR create a new one.'
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # If not superuser, hide company field or limit queryset?
        # For this requirement, we just auto-assign. We can hide it from the form or leave standard.
        return form

    def get_email(self, obj):
        return obj.user.email if obj.user else obj.email
    get_email.short_description = 'Email'

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('create_user'):
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            first_name = form.cleaned_data.get('first_name') or ""
            last_name = form.cleaned_data.get('last_name') or ""
            email = form.cleaned_data.get('email') or ""

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                company=request.user.company if hasattr(request.user, 'company') else None
            )
            obj.user = user
            
            # Assign Role
            role = form.cleaned_data.get('role')
            if role:
                UserRole.objects.create(user=user, role=role)

            # Model logic checks if obj.user is set and clears first_name/last_name/email
        
        # Handle updates to existing user
        elif change and obj.user:
            user = obj.user
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            
            # Update username if provided (and creating user logic didn't run)
            if form.cleaned_data.get('username'):
                 user.username = form.cleaned_data.get('username')
            
            # Update password if provided
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            
            user.save()

            # Update Role
            role = form.cleaned_data.get('role')
            if role:
                # Remove old roles? Or just update/create.
                # Project seems assuming single role from the form behavior
                UserRole.objects.filter(user=user).delete() # clear old
                UserRole.objects.create(user=user, role=role)
            else:
                 # If role cleared in form, remove it?
                 UserRole.objects.filter(user=user).delete()

        # Assign company to Employee if not set
        if not obj.company and hasattr(request.user, 'company'):
            obj.company = request.user.company

        super().save_model(request, obj, form, change)

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'department')
    search_fields = ('name', 'slug')
    list_filter = ('department',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__user__first_name', 'employee__user__last_name', 'employee__user__username')
    list_filter = ('date', 'status')


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_days_per_year', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'approved_by')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__user__first_name', 'employee__user__last_name', 'employee__user__username', 'leave_type__name')
    list_filter = ('status', 'leave_type', 'start_date', 'end_date', 'is_active')
