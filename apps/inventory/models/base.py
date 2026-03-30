# inventory/models/base.py

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import uuid


class BaseMasterModel(models.Model):
    name = models.CharField(_("name"), max_length=120)
    code = models.CharField(_("code"), max_length=50, unique=True, blank=True)
    slug = models.SlugField(_("slug"), max_length=100, unique=True, blank=True)

    is_active = models.BooleanField(_("is active"), default=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}"

    def _build_slug(self):
        return slugify(self.name) or self.__class__.__name__.lower()

    def clean(self):
        super().clean()
        if self.name:
            self.slug = self._build_slug()

        if self.slug:
            queryset = self.__class__.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError(
                    {"name": _("This %(model)s already exists.") % {"model": self._meta.verbose_name}}
                )

    def save(self, *args, **kwargs):
        self.slug = self._build_slug()
        if not self.code:
            prefix = self.__class__.__name__[:3].upper()
            random_part = str(uuid.uuid4())[:6].upper()
            self.code = f"{prefix}-{random_part}"
        super().save(*args, **kwargs)
