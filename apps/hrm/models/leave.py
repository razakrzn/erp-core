from django.db import models
from django.utils.translation import gettext_lazy as _

class LeaveType(models.Model):
    name = models.CharField(_("name"), max_length=100)
    max_days_per_year = models.IntegerField(_("max days per year"))
    is_active = models.BooleanField(_("is active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("leave type")
        verbose_name_plural = _("leave types")
        ordering = ['name']

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    employee = models.ForeignKey("hrm.Employee", verbose_name=_("employee"), on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey("hrm.LeaveType", verbose_name=_("leave type"), on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))
    status = models.CharField(_("status"), max_length=50, default="pending")
    approved_by = models.ForeignKey("accounts.User", verbose_name=_("approved by"), null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_leaves')
    is_active = models.BooleanField(_("is active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("leave request")
        verbose_name_plural = _("leave requests")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"
