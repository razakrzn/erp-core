from django.conf import settings
from django.db import models
from django.db.models import IntegerField
from django.db.models.functions import Cast, Substr
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ─────────────────────────────────────────────────────────────────────────────
# Project
# ─────────────────────────────────────────────────────────────────────────────


class Project(models.Model):
    STATUS_CHOICES = [
        ("quotation_approved", "Quotation Approved"),
        ("planning", "Planning"),
        ("in_production", "In Production"),
        ("quality_check", "Quality Check"),
        ("ready_for_delivery", "Ready for Delivery"),
        ("delivery_in_progress", "Delivery in Progress"),
        ("installation", "Installation"),
        ("installation_completed", "Installation Completed"),
        ("snagging", "Snagging"),
        ("on_hold", "On Hold"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    # Auto-generated JO-YYYY-NNN
    job_number = models.CharField(_("job number"), max_length=30, unique=True, blank=True, editable=False)

    # Assessment links
    quote = models.OneToOneField(
        "assessment.Quote",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project",
    )
    boq = models.ForeignKey(
        "assessment.Boq",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )

    # Client
    client = models.ForeignKey(
        "crm.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )

    # Core
    project_name = models.CharField(_("project name"), max_length=255)
    description = models.TextField(_("description"), blank=True, default="")
    location = models.CharField(_("location"), max_length=500, blank=True, default="")
    status = models.CharField(_("status"), max_length=30, choices=STATUS_CHOICES, default="quotation_approved")

    # Timeline
    start_date = models.DateField(_("start date"), null=True, blank=True)
    end_date = models.DateField(_("end date"), null=True, blank=True)
    actual_end_date = models.DateField(_("actual end date"), null=True, blank=True)

    # Financials
    contract_value = models.DecimalField(_("contract value"), max_digits=15, decimal_places=2, default=0)

    # Team lead — quick FK; full team in ProjectTeamMember
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_projects",
    )

    # Audit
    is_active = models.BooleanField(_("is active"), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_projects",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")
        ordering = ["-created_at"]

    def _generate_job_number(self):
        year = timezone.now().year
        prefix = f"JO-{year}-"
        last = (
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
        ("project_manager", "Project Manager"),
        ("site_supervisor", "Site Supervisor"),
        ("lead_carpenter", "Lead Carpenter"),
        ("carpenter", "Carpenter"),
        ("painter", "Painter"),
        ("electrician", "Electrician"),
        ("logistics", "Logistics Coordinator"),
        ("qa_inspector", "QA Inspector"),
        ("installer", "Installer"),
        ("designer", "Designer"),
        ("draftsman", "Draftsman"),
        ("procurement", "Procurement Officer"),
        ("other", "Other"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="team_members")
    employee = models.ForeignKey(
        "hrm.Employee",
        on_delete=models.CASCADE,
        related_name="project_assignments",
        help_text="Select from the HRM employee roster.",
    )
    designation = models.ForeignKey(
        "hrm.Designation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_team_members",
        help_text="Auto-filled from employee's HRM designation; can be overridden.",
    )
    role_in_project = models.CharField(_("role in project"), max_length=25, choices=ROLE_CHOICES, default="other")
    custom_role = models.CharField(
        _("custom role"),
        max_length=100,
        blank=True,
        default="",
        help_text="Used when role_in_project = 'other'.",
    )
    allocated_from = models.DateField(_("allocated from"), null=True, blank=True)
    allocated_to = models.DateField(_("allocated to"), null=True, blank=True)
    is_active = models.BooleanField(_("is active"), default=True)
    allocation_pct = models.PositiveSmallIntegerField(
        _("allocation %"),
        default=100,
        help_text="Percentage of working time allocated to this project.",
    )
    notes = models.TextField(_("notes"), blank=True, default="")
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_project_team_members",
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



