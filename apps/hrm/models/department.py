from django.db import models
from django.utils.translation import gettext_lazy as _

from django.utils.text import slugify

class Department(models.Model):
    name = models.CharField(_("name"), max_length=100, unique=True)
    slug = models.SlugField(_("slug"), max_length=100, unique=True, blank=True)
    head = models.ForeignKey('hrm.Employee', verbose_name=_("head"), null=True, blank=True, on_delete=models.SET_NULL, related_name='headed_departments')
    is_active = models.BooleanField(_("is active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("department")
        verbose_name_plural = _("departments")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)