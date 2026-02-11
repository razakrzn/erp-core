from django.db import models
from django.utils.translation import gettext_lazy as _

class Company(models.Model):
    name = models.CharField(_("name"), max_length=200)
    # unique=True handles the index; uppercase logic moved to save()
    code = models.CharField(_("code"), max_length=50, unique=True)
    is_active = models.BooleanField(_("is active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("companies")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        self.code = self.code.upper().strip()
        super().save(*args, **kwargs)