from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.hrm.models.department import Department
from apps.hrm.models.attendance import Attendance
from apps.hrm.models.employee import Employee, PreviousEmployment
from apps.rbac.models import Role, UserRole

User = get_user_model()

class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'slug', 'head', 'head_name', 'is_active', 'created_at']
        read_only_fields = ['slug', 'created_at']

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

class PreviousEmploymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreviousEmployment
        fields = ['id', 'company_name', 'designation', 'start_date', 'end_date', 'reason_for_leaving', 'experience_certificate_attached']

class EmployeeListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_name = serializers.CharField(source='designation.name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'email', 'full_name', 'job_title', 
            'designation_name', 'department_name', 'mobile_number'
        ]

class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_name = serializers.CharField(source='designation.name', read_only=True)
    previous_employments = PreviousEmploymentSerializer(many=True, required=False)

    # Fields for User creation
    create_user = serializers.BooleanField(write_only=True, required=False, default=False)
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True, required=False)

    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'email', 'full_name',
            'department', 'department_name', 'designation', 'designation_name',
            'is_active', 'created_at',
            'create_user', 'username', 'password', 'role',
            # Personal Information
            'profile_photo', 'gender', 'date_of_birth', 'nationality', 'mobile_number',
            'current_address_uae', 'permanent_address_home_country',
            # Emergency Contact
            'emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone', 'emergency_contact_home_country_phone',
            # Passport and Visa
            'passport_number', 'passport_issue_date', 'passport_expiry_date', 'passport_place_of_issue',
            'uae_visa_type', 'visa_number', 'uid_number', 'visa_issue_date', 'visa_expiry_date',
            'emirates_id_number', 'emirates_id_expiry_date', 'labor_card_number',
            # Employment
            'job_title', 'employment_type', 'offer_letter_reference_number', 'contract_type',
            'probation_period_months', 'date_of_joining', 'work_location',
            # Work Schedule
            'working_days', 'working_hours', 'overtime_eligible',
            # Salary
            'basic_salary', 'housing_allowance', 'transport_allowance', 'other_allowances', 'total_salary',
            'bank_name', 'iban_number', 'account_number', 'salary_payment_cycle',
            # Health
            'blood_group', 'medical_conditions', 'allergies', 'medical_insurance_provider', 'policy_number',
            # Education
            'highest_qualification', 'institution_name', 'year_of_graduation', 'attestation_status', 'certifications',
            # IT Assets
            'laptop_allocated', 'sim_card_allocated', 'access_card_allocated', 'biometric_registration_done',
            # Declaration
            'employee_signature', 'signature_date', 'hr_signature',
            # Nested
            'previous_employments'
        ]
        read_only_fields = ['created_at']

    def validate(self, attrs):
        create_user = attrs.get('create_user')
        if create_user:
            if not attrs.get('username'):
                raise serializers.ValidationError({"username": "Username is required when creating a user."})
            if not attrs.get('password'):
                raise serializers.ValidationError({"password": "Password is required when creating a user."})
            if not attrs.get('email'):
                raise serializers.ValidationError({"email": "Email is required when creating a user."})
            if not attrs.get('role'):
                raise serializers.ValidationError({"role": "Role is required when creating a user."})
            
            # Check uniqueness
            if User.objects.filter(username=attrs.get('username')).exists():
                raise serializers.ValidationError({"username": "Username already exists."})
            if User.objects.filter(email=attrs.get('email')).exists():
                 raise serializers.ValidationError({"email": "Email already exists."})

        return attrs

    def create(self, validated_data):
        previous_employments_data = validated_data.pop('previous_employments', [])
        create_user = validated_data.pop('create_user', False)
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)
        role = validated_data.pop('role', None)
        
        # Get Company from context (passed from view)
        request = self.context.get('request')
        company = None
        if request and hasattr(request.user, 'company'):
            company = request.user.company

        validated_data['company'] = company

        with transaction.atomic():
            if create_user:
                # Create User
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=validated_data.get('email'),
                    first_name=validated_data.get('first_name', ''),
                    last_name=validated_data.get('last_name', ''),
                    company=company
                )
                
                # Assign Role
                if role:
                    UserRole.objects.create(user=user, role=role)
                
                # Create Employee
                employee = Employee.objects.create(user=user, **validated_data)
            else:
                # Create Employee without User
                employee = Employee.objects.create(**validated_data)

            # Handle Previous Employments
            for pe_data in previous_employments_data:
                PreviousEmployment.objects.create(employee=employee, **pe_data)
        
        return employee

    def update(self, instance, validated_data):
        previous_employments_data = validated_data.pop('previous_employments', None)
        
        request = self.context.get('request')
        company = None
        if request and hasattr(request.user, 'company'):
            company = request.user.company
            
        instance.company = company 
        
        if instance.user:
            user = instance.user
            user.first_name = validated_data.get('first_name', user.first_name)
            user.last_name = validated_data.get('last_name', user.last_name)
            user.email = validated_data.get('email', user.email)
            user.save()
        
        # Update Employee fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle Previous Employments (Full replacement logic for simplicity)
        if previous_employments_data is not None:
            instance.previous_employments.all().delete()
            for pe_data in previous_employments_data:
                PreviousEmployment.objects.create(employee=instance, **pe_data)
        
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # If linked to user, ensure we show the user's details if local fields are empty
        if instance.user:
            ret['first_name'] = instance.user.first_name
            ret['last_name'] = instance.user.last_name
            ret['email'] = instance.user.email
        return ret
