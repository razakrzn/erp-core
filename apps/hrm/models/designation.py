from django.db import models
from django.utils.translation import gettext_lazy as _

class Designation(models.Model):
    name = models.CharField(_("name"), max_length=100)
    code = models.CharField(_("code"), max_length=50, unique=True)
    department = models.ForeignKey('hrm.Department', verbose_name=_("department"), on_delete=models.CASCADE, related_name='designations')
    head = models.ForeignKey('hrm.Employee', verbose_name=_("head"), null=True, blank=True, on_delete=models.SET_NULL, related_name='headed_designations')
    is_active = models.BooleanField(_("is active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("designation")
        verbose_name_plural = _("designations")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.code = self.code.upper().strip()
        super().save(*args, **kwargs)