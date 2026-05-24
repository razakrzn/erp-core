from django.conf import settings
from django.db import models
from django.db.models import IntegerField
from django.db.models.functions import Cast, Substr
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ─── upload helpers ──────────────────────────────────────────────────────────

def _doc_upload(instance, filename):
    return f"projects/{instance.project_id}/documents/{filename}"

def _site_photo_upload(instance, filename):
    return f"projects/{instance.site_log.project_id}/site_logs/{filename}"

def _dxf_upload(instance, filename):
    return f"projects/{instance.project_id}/dxf/{filename}"

def _delivery_doc_upload(instance, filename):
    return f"projects/{instance.project_id}/delivery/{filename}"


# ─────────────────────────────────────────────────────────────────────────────
# Project
# ─────────────────────────────────────────────────────────────────────────────

class Project(models.Model):
    STATUS_CHOICES = [
        ("quotation_approved",     "Quotation Approved"),
        ("planning",               "Planning"),
        ("in_production",          "In Production"),
        ("quality_check",          "Quality Check"),
        ("ready_for_delivery",     "Ready for Delivery"),
        ("delivery_in_progress",   "Delivery in Progress"),
        ("installation",           "Installation"),
        ("installation_completed", "Installation Completed"),
        ("snagging",               "Snagging"),
        ("on_hold",                "On Hold"),
        ("cancelled",              "Cancelled"),
        ("completed",              "Completed"),
    ]

    # Auto-generated JO-YYYY-NNN
    job_number = models.CharField(
        _("job number"), max_length=30, unique=True, blank=True, editable=False
    )

    # Assessment links
    quote = models.OneToOneField(
        "assessment.Quote", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="project",
    )
    boq = models.ForeignKey(
        "assessment.Boq", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="projects",
    )

    # Client
    client = models.ForeignKey(
        "crm.Customer", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="projects",
    )

    # Core
    project_name   = models.CharField(_("project name"), max_length=255)
    description    = models.TextField(_("description"), blank=True, default="")
    location       = models.CharField(_("location"), max_length=500, blank=True, default="")
    status         = models.CharField(
        _("status"), max_length=30, choices=STATUS_CHOICES, default="quotation_approved"
    )

    # Timeline
    start_date      = models.DateField(_("start date"), null=True, blank=True)
    end_date        = models.DateField(_("end date"), null=True, blank=True)
    actual_end_date = models.DateField(_("actual end date"), null=True, blank=True)

    # Financials
    contract_value  = models.DecimalField(_("contract value"), max_digits=15, decimal_places=2, default=0)

    # Team lead — quick FK; full team in ProjectTeamMember
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="managed_projects",
    )

    # Audit
    is_active  = models.BooleanField(_("is active"), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="created_projects",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="updated_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")
        ordering = ["-created_at"]

    def _generate_job_number(self):
        year   = timezone.now().year
        prefix = f"JO-{year}-"
        last   = (
            Project.objects.filter(job_number__startswith=prefix)
            .annotate(num=Cast(Substr("job_number", len(prefix) + 1), IntegerField()))
            .order_by("-num")
            .first()
        )
        return f"{prefix}{((last.num if last else 0) + 1):03d}"

    def save(self, *args, **kwargs):
        if not self.job_number:
            self.job_number = self._generate_job_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.job_number} – {self.project_name}"


# ─────────────────────────────────────────────────────────────────────────────
# ProjectTeamMember  (NEW — team allocation)
# ─────────────────────────────────────────────────────────────────────────────

class ProjectTeamMember(models.Model):
    ROLE_CHOICES = [
        ("project_manager",  "Project Manager"),
        ("site_supervisor",  "Site Supervisor"),
        ("lead_carpenter",   "Lead Carpenter"),
        ("carpenter",        "Carpenter"),
        ("painter",          "Painter"),
        ("electrician",      "Electrician"),
        ("logistics",        "Logistics Coordinator"),
        ("qa_inspector",     "QA Inspector"),
        ("installer",        "Installer"),
        ("designer",         "Designer"),
        ("draftsman",        "Draftsman"),
        ("procurement",      "Procurement Officer"),
        ("other",            "Other"),
    ]

    project    = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="team_members"
    )
    employee   = models.ForeignKey(
        "hrm.Employee", on_delete=models.CASCADE, related_name="project_assignments",
        help_text="Select from the HRM employee roster.",
    )
    designation = models.ForeignKey(
        "hrm.Designation", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="project_team_members",
        help_text="Auto-filled from employee's HRM designation; can be overridden.",
    )
    role_in_project = models.CharField(
        _("role in project"), max_length=25, choices=ROLE_CHOICES, default="other"
    )
    custom_role = models.CharField(
        _("custom role"), max_length=100, blank=True, default="",
        help_text="Used when role_in_project = 'other'.",
    )
    allocated_from = models.DateField(_("allocated from"), null=True, blank=True)
    allocated_to   = models.DateField(_("allocated to"),   null=True, blank=True)
    is_active      = models.BooleanField(_("is active"), default=True)
    allocation_pct = models.PositiveSmallIntegerField(
        _("allocation %"), default=100,
        help_text="Percentage of working time allocated to this project.",
    )
    notes = models.TextField(_("notes"), blank=True, default="")
    added_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="added_project_team_members",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("project team member")
        verbose_name_plural = _("project team members")
        ordering = ["role_in_project", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("project", "employee"),
                name="uniq_project_employee",
            )
        ]

    def save(self, *args, **kwargs):
        if not self.designation_id and self.employee_id:
            try:
                self.designation = self.employee.designation
            except Exception:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project.job_number} | {self.employee} | {self.get_role_in_project_display()}"


# ─────────────────────────────────────────────────────────────────────────────
# Milestone
# ─────────────────────────────────────────────────────────────────────────────

class Milestone(models.Model):
    STATUS_CHOICES = [
        ("pending",     "Pending"),
        ("in_progress", "In Progress"),
        ("completed",   "Completed"),
        ("delayed",     "Delayed"),
    ]

    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    start_date  = models.DateField(null=True, blank=True)
    due_date    = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    completion_percentage = models.PositiveSmallIntegerField(default=0)
    order       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("milestone")
        verbose_name_plural = _("milestones")
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.project.job_number} | {self.name}"


# ─────────────────────────────────────────────────────────────────────────────
# Task
# ─────────────────────────────────────────────────────────────────────────────

class Task(models.Model):
    PRIORITY_CHOICES = [
        ("low","Low"), ("medium","Medium"), ("high","High"), ("critical","Critical"),
    ]
    STATUS_CHOICES = [
        ("todo","To Do"), ("in_progress","In Progress"),
        ("review","Review"), ("done","Done"), ("blocked","Blocked"),
    ]

    project     = models.ForeignKey(Project,   on_delete=models.CASCADE, related_name="tasks")
    milestone   = models.ForeignKey(
        Milestone, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="project_tasks",
    )
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    status      = models.CharField(max_length=15, choices=STATUS_CHOICES, default="todo")
    start_date  = models.DateField(null=True, blank=True)
    due_date    = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    completion_percentage = models.PositiveSmallIntegerField(default=0)
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="created_project_tasks",
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("task")
        verbose_name_plural = _("tasks")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────────────────────
# SiteLog + SiteLogPhoto
# ─────────────────────────────────────────────────────────────────────────────

class SiteLog(models.Model):
    WEATHER_CHOICES = [
        ("sunny","Sunny"), ("cloudy","Cloudy"), ("rainy","Rainy"), ("stormy","Stormy"),
    ]

    project       = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="site_logs")
    date          = models.DateField()
    weather       = models.CharField(max_length=20, choices=WEATHER_CHOICES, blank=True, default="")
    temperature   = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    workers_count = models.PositiveIntegerField(default=0)
    summary       = models.TextField()
    challenges    = models.TextField(blank=True, default="")
    next_day_plan = models.TextField(blank=True, default="")
    logged_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="project_site_logs",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("site log")
        verbose_name_plural = _("site logs")
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=("project", "date"), name="uniq_project_site_log_date")
        ]

    def __str__(self):
        return f"{self.project.job_number} | {self.date}"


class SiteLogPhoto(models.Model):
    site_log    = models.ForeignKey(SiteLog, on_delete=models.CASCADE, related_name="photos")
    photo       = models.ImageField(upload_to=_site_photo_upload)
    caption     = models.CharField(max_length=255, blank=True, default="")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]


# ─────────────────────────────────────────────────────────────────────────────
# Timesheet
# ─────────────────────────────────────────────────────────────────────────────

class Timesheet(models.Model):
    project        = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="timesheets")
    employee       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_timesheets"
    )
    task           = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    date           = models.DateField()
    hours_worked   = models.DecimalField(max_digits=5, decimal_places=2)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    description    = models.TextField(blank=True, default="")
    approved       = models.BooleanField(default=False)
    approved_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="approved_project_timesheets",
    )
    approved_at    = models.DateTimeField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.employee} | {self.project.job_number} | {self.date}"


# ─────────────────────────────────────────────────────────────────────────────
# ProjectDocument
# ─────────────────────────────────────────────────────────────────────────────

class ProjectDocument(models.Model):
    DOC_TYPE_CHOICES = [
        ("drawing","Drawing"), ("permit","Permit"), ("contract","Contract"),
        ("report","Report"), ("sign_off","Sign-Off Sheet"),
        ("specification","Specification"), ("photo","Photo"), ("other","Other"),
    ]

    project       = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    name          = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES, default="other")
    file          = models.FileField(upload_to=_doc_upload)
    version       = models.CharField(max_length=20, blank=True, default="")
    description   = models.TextField(blank=True, default="")
    uploaded_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="project_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.job_number} | {self.name}"


# ─────────────────────────────────────────────────────────────────────────────
# ProjectMaterial  (NEW — material allocation from inventory)
# ─────────────────────────────────────────────────────────────────────────────

class ProjectMaterial(models.Model):
    STATUS_CHOICES = [
        ("planned",   "Planned"),
        ("requested", "Purchase Requested"),
        ("ordered",   "Ordered"),
        ("received",  "Received"),
        ("issued",    "Issued to Production"),
        ("returned",  "Returned"),
    ]

    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="materials")
    product     = models.ForeignKey(
        "inventory.Product", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="project_materials",
    )
    material_name = models.CharField(max_length=255, blank=True, default="")
    description   = models.TextField(blank=True, default="")
    unit          = models.CharField(max_length=50, blank=True, default="")
    quantity_required  = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    quantity_received  = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    quantity_issued    = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    unit_cost     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status        = models.CharField(max_length=15, choices=STATUS_CHOICES, default="planned")
    required_by   = models.DateField(null=True, blank=True)
    milestone     = models.ForeignKey(
        Milestone, on_delete=models.SET_NULL, null=True, blank=True, related_name="materials"
    )
    notes         = models.TextField(blank=True, default="")
    created_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="created_project_materials",
    )
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("project material")
        verbose_name_plural = _("project materials")
        ordering = ["-created_at"]

    @property
    def total_cost(self):
        return (self.quantity_required or 0) * (self.unit_cost or 0)

    def __str__(self):
        name = self.product.name if self.product else self.material_name
        return f"{self.project.job_number} | {name}"


# ─────────────────────────────────────────────────────────────────────────────
# QualityCheckpoint  (NEW — QA gate per milestone/stage)
# ─────────────────────────────────────────────────────────────────────────────

class QualityCheckpoint(models.Model):
    RESULT_CHOICES = [
        ("pending",  "Pending"),
        ("pass",     "Pass"),
        ("fail",     "Fail"),
        ("rework",   "Rework Required"),
        ("waived",   "Waived"),
    ]

    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="quality_checkpoints")
    milestone   = models.ForeignKey(
        Milestone, on_delete=models.SET_NULL, null=True, blank=True, related_name="quality_checkpoints"
    )
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    checklist   = models.JSONField(
        default=list, blank=True,
        help_text='List of {"item": str, "checked": bool} dicts.',
    )
    result      = models.CharField(max_length=10, choices=RESULT_CHOICES, default="pending")
    inspected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="inspected_checkpoints",
    )
    inspection_date = models.DateField(null=True, blank=True)
    remarks     = models.TextField(blank=True, default="")
    photo       = models.ImageField(upload_to="projects/qa/", null=True, blank=True)
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="created_quality_checkpoints",
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("quality checkpoint")
        verbose_name_plural = _("quality checkpoints")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.job_number} | QA | {self.title}"


# ─────────────────────────────────────────────────────────────────────────────
# DeliverySchedule  (NEW)
# ─────────────────────────────────────────────────────────────────────────────

class DeliverySchedule(models.Model):
    STATUS_CHOICES = [
        ("scheduled",   "Scheduled"),
        ("in_transit",  "In Transit"),
        ("delivered",   "Delivered"),
        ("failed",      "Failed"),
        ("rescheduled", "Rescheduled"),
    ]

    project            = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="deliveries")
    batch_number       = models.CharField(max_length=50, blank=True, default="")
    scheduled_date     = models.DateField()
    actual_date        = models.DateField(null=True, blank=True)
    status             = models.CharField(max_length=15, choices=STATUS_CHOICES, default="scheduled")
    delivery_address   = models.TextField(blank=True, default="")
    driver             = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="project_deliveries",
    )
    vehicle_info       = models.CharField(max_length=100, blank=True, default="")
    items_description  = models.TextField(blank=True, default="")
    delivery_note_file = models.FileField(upload_to=_delivery_doc_upload, null=True, blank=True)
    client_received    = models.BooleanField(default=False)
    client_signature   = models.ImageField(upload_to="projects/delivery/signatures/", null=True, blank=True)
    notes              = models.TextField(blank=True, default="")
    created_by         = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="created_deliveries",
    )
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("delivery schedule")
        verbose_name_plural = _("delivery schedules")
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.project.job_number} | Delivery {self.batch_number} | {self.scheduled_date}"


# ─────────────────────────────────────────────────────────────────────────────
# ReworkRequest
# ─────────────────────────────────────────────────────────────────────────────

class ReworkRequest(models.Model):
    STATUS_CHOICES   = [("open","Open"), ("in_progress","In Progress"), ("resolved","Resolved"), ("closed","Closed")]
    SEVERITY_CHOICES = [("minor","Minor"), ("major","Major"), ("critical","Critical")]

    project          = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="rework_requests")
    task             = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    quality_checkpoint = models.ForeignKey(
        QualityCheckpoint, on_delete=models.SET_NULL, null=True, blank=True, related_name="rework_requests"
    )
    title            = models.CharField(max_length=255)
    description      = models.TextField()
    severity         = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="minor")
    status           = models.CharField(max_length=15, choices=STATUS_CHOICES,   default="open")
    raised_by        = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="raised_reworks"
    )
    assigned_to      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_reworks"
    )
    resolved_at      = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, default="")
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("rework request")
        verbose_name_plural = _("rework requests")
        ordering = ["-created_at"]


# ─────────────────────────────────────────────────────────────────────────────
# InstallationLog
# ─────────────────────────────────────────────────────────────────────────────

class InstallationLog(models.Model):
    STATUS_CHOICES = [
        ("scheduled","Scheduled"), ("in_progress","In Progress"),
        ("completed","Completed"), ("snag_raised","Snag Raised"),
    ]

    project          = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="installation_logs")
    install_date     = models.DateField()
    location_detail  = models.CharField(max_length=500, blank=True, default="")
    status           = models.CharField(max_length=15, choices=STATUS_CHOICES, default="scheduled")
    team_lead        = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="led_installations"
    )
    workers_count    = models.PositiveIntegerField(default=0)
    items_installed  = models.TextField(blank=True, default="")
    notes            = models.TextField(blank=True, default="")
    client_sign_off  = models.BooleanField(default=False)
    sign_off_date    = models.DateField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("installation log")
        verbose_name_plural = _("installation logs")
        ordering = ["-install_date"]


# ─────────────────────────────────────────────────────────────────────────────
# DXFFile + DXFAnalysisResult
# ─────────────────────────────────────────────────────────────────────────────

class DXFFile(models.Model):
    STATUS_CHOICES = [
        ("uploaded","Uploaded"), ("processing","Processing"),
        ("completed","Completed"), ("failed","Failed"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="dxf_files")
    file = models.FileField(upload_to=_dxf_upload)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="uploaded")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="uploaded_dxf_files"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("dxf file")
        verbose_name_plural = _("dxf files")
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.project.job_number} | {self.file.name}"


class DXFAnalysisResult(models.Model):
    dxf_file = models.OneToOneField(DXFFile, on_delete=models.CASCADE, related_name="analysis_result")
    total_parts = models.PositiveIntegerField(default=0)
    placed_parts = models.PositiveIntegerField(default=0)
    unplaced_parts = models.PositiveIntegerField(default=0)
    oversized_parts = models.PositiveIntegerField(default=0)
    utilization_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    raw_data = models.JSONField(default=dict, blank=True, help_text="Detailed results including parts, bins, placements, and summaries.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("dxf analysis result")
        verbose_name_plural = _("dxf analysis results")

    def __str__(self):
        return f"Analysis of {self.dxf_file.file.name}"
