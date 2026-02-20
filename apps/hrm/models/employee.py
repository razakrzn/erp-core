from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        null=True,
        blank=True
    )
    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="employees",
        null=True,
        blank=True,
    )
    
    # Personal Information
    first_name = models.CharField(_("first name"), max_length=100, null=True, blank=True)
    last_name = models.CharField(_("last name"), max_length=100, null=True, blank=True)
    email = models.EmailField(_("email address"), unique=True, null=True, blank=True)
    profile_photo = models.ImageField(_("profile photo"), upload_to='employees/photos/', null=True, blank=True)
    
    class Gender(models.TextChoices):
        MALE = 'Male', _('Male')
        FEMALE = 'Female', _('Female')
        OTHER = 'Other', _('Other')

    gender = models.CharField(_("gender"), max_length=10, choices=Gender.choices, null=True, blank=True)
    date_of_birth = models.DateField(_("date of birth"), null=True, blank=True)
    nationality = models.CharField(_("nationality"), max_length=100, null=True, blank=True)
    mobile_number = models.CharField(_("mobile number"), max_length=20, null=True, blank=True)
    current_address_uae = models.TextField(_("current address UAE"), null=True, blank=True)
    permanent_address_home_country = models.TextField(_("permanent address home country"), null=True, blank=True)

    # Emergency Contact
    emergency_contact_name = models.CharField(_("emergency contact name"), max_length=100, null=True, blank=True)
    emergency_contact_relationship = models.CharField(_("relationship"), max_length=50, null=True, blank=True)
    emergency_contact_phone = models.CharField(_("emergency contact phone"), max_length=20, null=True, blank=True)
    emergency_contact_home_country_phone = models.CharField(_("home country phone"), max_length=20, null=True, blank=True)

    # Passport and Visa Details
    passport_number = models.CharField(_("passport number"), max_length=50, null=True, blank=True)
    passport_issue_date = models.DateField(_("passport issue date"), null=True, blank=True)
    passport_expiry_date = models.DateField(_("passport expiry date"), null=True, blank=True)
    passport_place_of_issue = models.CharField(_("place of issue"), max_length=100, null=True, blank=True)
    
    class VisaType(models.TextChoices):
        TOURIST_30_SINGLE = "TOURIST_30_SINGLE", _("Tourist Visa - 30 Days (Single Entry)")
        TOURIST_30_MULTI = "TOURIST_30_MULTI", _("Tourist Visa - 30 Days (Multiple Entry)")
        
        TOURIST_60_SINGLE = "TOURIST_60_SINGLE", _("Tourist Visa - 60 Days (Single Entry)")
        TOURIST_60_MULTI = "TOURIST_60_MULTI", _("Tourist Visa - 60 Days (Multiple Entry)")
    
        TOURIST_5_YEAR_MULTI = "TOURIST_5_YEAR_MULTI", _("5-Year Multiple Entry Tourist Visa")
    
        TRANSIT_48 = "TRANSIT_48", _("Transit Visa - 48 Hours")
        TRANSIT_96 = "TRANSIT_96", _("Transit Visa - 96 Hours")
    
        VISIT_FAMILY = "VISIT_FAMILY", _("Visit Visa for Family/Friends")
        VISA_ON_ARRIVAL = "VISA_ON_ARRIVAL", _("Visa on Arrival")

        # =========================
        # Residence Visas
        # =========================
        EMPLOYMENT = "EMPLOYMENT", _("Employment Visa (Work Visa)")
        INVESTOR = "INVESTOR", _("Investor Visa")
        PARTNER = "PARTNER", _("Partner Visa")
        FREELANCER = "FREELANCER", _("Freelancer Visa")
        REMOTE_WORK = "REMOTE_WORK", _("Remote Work Visa")
        GREEN = "GREEN", _("Green Visa")
        GOLDEN = "GOLDEN", _("Golden Visa")
        PROPERTY_OWNER = "PROPERTY_OWNER", _("Property Owner Visa")
        RETIREMENT = "RETIREMENT", _("Retirement Visa")
        STUDENT = "STUDENT", _("Student Visa")
        DEPENDENT = "DEPENDENT", _("Dependent Visa (Spouse/Children/Parents)")
        DOMESTIC_WORKER = "DOMESTIC_WORKER", _("Domestic Worker Visa")

        # =========================
        # Special Visas
        # =========================
        MEDICAL = "MEDICAL", _("Medical Treatment Visa")
        PATIENT_COMPANION = "PATIENT_COMPANION", _("Patient Companion Visa")
        CONFERENCE = "CONFERENCE", _("Conference / Event Visa")
        MISSION = "MISSION", _("Mission Visa (Short-term Work Permit)")
        CREW = "CREW", _("Crew Visa")


    uae_visa_type = models.CharField(_("UAE visa type"), max_length=50, choices=VisaType.choices, null=True, blank=True)
    visa_number = models.CharField(_("visa number"), max_length=50, null=True, blank=True)
    uid_number = models.CharField(_("UID number"), max_length=50, null=True, blank=True)
    visa_issue_date = models.DateField(_("visa issue date"), null=True, blank=True)
    visa_expiry_date = models.DateField(_("visa expiry date"), null=True, blank=True)
    emirates_id_number = models.CharField(_("Emirates ID number"), max_length=50, null=True, blank=True)
    emirates_id_expiry_date = models.DateField(_("Emirates ID expiry date"), null=True, blank=True)
    labor_card_number = models.CharField(_("labor card number"), max_length=50, null=True, blank=True)

    # Employment Details
    department = models.ForeignKey('hrm.Department', verbose_name=_("department"), on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    designation = models.ForeignKey('hrm.Designation', verbose_name=_("designation"), on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    
    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", _("Full-time")
        PART_TIME = "PART_TIME", _("Part-time")
        TEMPORARY = "TEMPORARY", _("Temporary")
        FLEXIBLE = "FLEXIBLE", _("Flexible Working")
        REMOTE = "REMOTE", _("Remote Work")
        JOB_SHARE = "JOB_SHARE", _("Job Sharing")


    employment_type = models.CharField(_("employment type"), max_length=50, choices=EmploymentType.choices, null=True, blank=True)
    offer_letter_reference_number = models.CharField(_("offer letter reference"), max_length=50, null=True, blank=True)
    
    class ContractType(models.TextChoices):

        # =========================
        # MOHRE Contracts (Mainland UAE)
        # =========================
        MOHRE_FIXED_TERM = "MOHRE_FIXED_TERM", _("MOHRE Standard Fixed-Term")
        MOHRE_PART_TIME = "MOHRE_PART_TIME", _("MOHRE Part-Time Contract")
        MOHRE_TEMPORARY = "MOHRE_TEMPORARY", _("MOHRE Temporary Contract")
        MOHRE_FLEXIBLE = "MOHRE_FLEXIBLE", _("MOHRE Flexible Contract")
        MOHRE_JOB_SHARE = "MOHRE_JOB_SHARE", _("MOHRE Job Sharing Contract")
        MOHRE_REMOTE = "MOHRE_REMOTE", _("MOHRE Remote Work Contract")

        # =========================
        # Free Zone Contracts
        # =========================
        FREEZONE_STANDARD = "FREEZONE_STANDARD", _("Free Zone Employment Contract")
        FREEZONE_FIXED = "FREEZONE_FIXED", _("Free Zone Fixed-Term Contract")

        # =========================
        # Limited / Unlimited (Legacy - Pre 2022 Reform)
        # =========================
        LIMITED = "LIMITED", _("Limited Contract (Legacy)")
        UNLIMITED = "UNLIMITED", _("Unlimited Contract (Legacy)")

        # =========================
        # Special Categories
        # =========================
        PROBATION = "PROBATION", _("Probationary Contract")
        CONSULTANCY = "CONSULTANCY", _("Consultancy / Service Contract")
        INTERNSHIP = "INTERNSHIP", _("Internship / Training Contract")


    contract_type = models.CharField(_("contract type"), max_length=100, choices=ContractType.choices, null=True, blank=True)
    probation_period_months = models.IntegerField(_("probation period (months)"), default=6, null=True, blank=True)
    date_of_joining = models.DateField(_("date of joining"), null=True, blank=True)
    
    class WorkLocation(models.TextChoices):
        FACTORY = 'Factory', _('Factory')
        SHOWROOM = 'Showroom', _('Showroom')
        OFFICE = 'Office', _('Office')
        SITE = 'Site', _('Site')
        WAREHOUSE = 'Warehouse', _('Warehouse')
        OTHER = 'Other', _('Other')

    work_location = models.CharField(_("work location"), max_length=50, choices=WorkLocation.choices, null=True, blank=True)
    
    # Work Schedule
    working_days = models.CharField(_("working days"), max_length=100, null=True, blank=True)
    working_hours = models.CharField(_("working hours"), max_length=50, null=True, blank=True)
    overtime_eligible = models.BooleanField(_("overtime eligible"), default=True)

    # Salary Details
    basic_salary = models.DecimalField(_("basic salary"), max_digits=10, decimal_places=2, default=0)
    housing_allowance = models.DecimalField(_("housing allowance"), max_digits=10, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(_("transport allowance"), max_digits=10, decimal_places=2, default=0)
    other_allowances = models.DecimalField(_("other allowances"), max_digits=10, decimal_places=2, default=0)
    total_salary = models.DecimalField(_("total salary"), max_digits=10, decimal_places=2, default=0)
    bank_name = models.CharField(_("bank name"), max_length=100, null=True, blank=True)
    iban_number = models.CharField(_("IBAN number"), max_length=50, null=True, blank=True)
    account_number = models.CharField(_("account number"), max_length=50, null=True, blank=True)
    salary_payment_cycle = models.CharField(_("salary payment cycle"), max_length=50, default='Monthly')

    # Health Data
    blood_group = models.CharField(_("blood group"), max_length=10, null=True, blank=True)
    medical_conditions = models.TextField(_("medical conditions"), null=True, blank=True)
    allergies = models.TextField(_("allergies"), null=True, blank=True)
    medical_insurance_provider = models.CharField(_("medical insurance provider"), max_length=100, null=True, blank=True)
    policy_number = models.CharField(_("policy number"), max_length=50, null=True, blank=True)

    # Education and Qualification
    highest_qualification = models.CharField(_("highest qualification"), max_length=100, null=True, blank=True)
    institution_name = models.CharField(_("institution name"), max_length=100, null=True, blank=True)
    year_of_graduation = models.IntegerField(_("year of graduation"), null=True, blank=True)
    attestation_status = models.CharField(_("attestation status"), max_length=50, null=True, blank=True)
    certifications = models.JSONField(_("certifications"), default=list, blank=True)

    # IT Assets Allocated
    laptop_allocated = models.BooleanField(_("laptop allocated"), default=False)
    sim_card_allocated = models.BooleanField(_("SIM card allocated"), default=False)
    access_card_allocated = models.BooleanField(_("access card allocated"), default=False)
    biometric_registration_done = models.BooleanField(_("biometric registration done"), default=False)

    # Declaration
    employee_signature = models.ImageField(_("employee signature"), upload_to='employees/signatures/', null=True, blank=True)
    signature_date = models.DateField(_("signature date"), null=True, blank=True)
    hr_signature = models.ImageField(_("HR signature"), upload_to='employees/signatures/', null=True, blank=True)

    is_active = models.BooleanField(_("is active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("employee")
        verbose_name_plural = _("employees")
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()} ({self.user.username})"
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        if self.user:
            return self.user.get_full_name()
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.user:
            # If user is linked, clear local fields to avoid duplication
            self.first_name = None
            self.last_name = None
            self.email = None
        else:
            # If no user, ensure email is normalized
            if self.email:
                self.email = self.email.lower().strip()
        super().save(*args, **kwargs)


class PreviousEmployment(models.Model):
    employee = models.ForeignKey(Employee, verbose_name=_("employee"), on_delete=models.CASCADE, related_name='previous_employments')
    company_name = models.CharField(_("company name"), max_length=100)
    # Mapping JSON 'designation' in PreviousEmployment
    designation = models.CharField(_("designation"), max_length=100)
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))
    reason_for_leaving = models.TextField(_("reason for leaving"), null=True, blank=True)
    experience_certificate_attached = models.BooleanField(_("experience certificate attached"), default=False)

    class Meta:
        verbose_name = _("previous employment")
        verbose_name_plural = _("previous employments")
