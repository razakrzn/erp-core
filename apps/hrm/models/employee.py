from django.db import models

from django.utils.translation import gettext_lazy as _

class Employee(models.Model):
    first_name = models.CharField(_("first name"), max_length=100)
    last_name = models.CharField(_("last name"), max_length=100)
    email = models.EmailField(_("email address"), unique=True)
    department = models.ForeignKey('hrm.Department', verbose_name=_("department"), on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    designation = models.ForeignKey('hrm.Designation', verbose_name=_("designation"), on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    is_active = models.BooleanField(_("is active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("employee")
        verbose_name_plural = _("employees")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower().strip()
        super().save(*args, **kwargs)
