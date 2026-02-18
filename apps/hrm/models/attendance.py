from django.db import models
from django.utils.translation import gettext_lazy as _

class Attendance(models.Model):
    employee = models.ForeignKey('hrm.Employee', verbose_name=_("employee"), on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(_("date"))
    check_in = models.TimeField(_("check in"), null=True, blank=True)
    check_out = models.TimeField(_("check out"), null=True, blank=True)
    status = models.CharField(_("status"), max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("attendance")
        verbose_name_plural = _("attendances")
        ordering = ['-date', '-check_in']

    def __str__(self):
        return f"{self.employee} - {self.date}"