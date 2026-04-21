from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.navigation.models import Feature, Module


class Company(models.Model):
    name = models.CharField(_("name"), max_length=200)
    # unique=True handles the index; uppercase logic moved to save()
    code = models.CharField(_("code"), max_length=50, unique=True)
    address = models.TextField(_("address"), blank=True, default="")
    phone = models.CharField(_("phone"), max_length=30, blank=True, default="")
    email = models.EmailField(_("email address"), blank=True, default="")
    website = models.CharField(_("website"), max_length=500, blank=True, default="")
    licence_number = models.CharField(_("licence number"), max_length=100, blank=True, default="")
    trn = models.CharField(_("trn"), max_length=100, blank=True, default="")
    logo = models.ImageField(_("company logo"), upload_to="companies/logos/", null=True, blank=True)
    is_active = models.BooleanField(_("is active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("companies")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        self.code = self.code.upper().strip()
        self.address = (self.address or "").strip()
        self.phone = (self.phone or "").strip()
        self.email = (self.email or "").lower().strip()
        self.website = (self.website or "").strip()
        self.licence_number = (self.licence_number or "").strip()
        self.trn = (self.trn or "").strip()
        super().save(*args, **kwargs)


class CompanyFeature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)


class CompanyModule(models.Model):
    """
    Company-level module override within an enabled feature.

    Modules are considered enabled by default whenever their parent feature is
    enabled for the company. This table stores explicit per-company overrides so
    individual modules can be disabled or re-enabled without changing the
    feature-level grant.
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("company module")
        verbose_name_plural = _("company modules")
        constraints = [
            models.UniqueConstraint(
                fields=["company", "module"],
                name="unique_company_module_access",
            )
        ]
