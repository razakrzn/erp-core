from django.db import models
from django.utils.translation import gettext_lazy as _


class TermsConditions(models.Model):
    title = models.CharField(_("title"), max_length=255)
    category = models.CharField(_("category"), max_length=150)
    content = models.TextField(_("content"))

    is_default = models.BooleanField(_("is default"), default=False)

    def __str__(self):
        return f"{self.title} - {self.category}"
