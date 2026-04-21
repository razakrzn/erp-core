from django.db import models
from django.utils.translation import gettext_lazy as _

from django.utils.text import slugify


class Designation(models.Model):
    name = models.CharField(_("name"), max_length=100, unique=True)
    slug = models.SlugField(_("slug"), max_length=100, unique=True, blank=True)
    department = models.ForeignKey(
        "hrm.Department", verbose_name=_("department"), on_delete=models.CASCADE, related_name="designations"
    )
    is_active = models.BooleanField(_("is active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("designation")
        verbose_name_plural = _("designations")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
