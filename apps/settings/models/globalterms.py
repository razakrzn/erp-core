from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class GlobalTerms(models.Model):
    title = models.CharField(_("title"), max_length=255)
    category = models.CharField(_("category"), max_length=150)
    content = models.TextField(_("content"))
    
    is_default = models.BooleanField(_("is default"), default=False)
    is_approved = models.BooleanField(_("is approved"), default=False)
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_global_terms",
        verbose_name=_("created by"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_global_terms",
        verbose_name=_("approved by"),
    )
    approved_at = models.DateTimeField(_("approved at"), null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.category}"
