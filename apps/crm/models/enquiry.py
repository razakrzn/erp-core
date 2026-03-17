from django.db import models
from django.utils.translation import gettext_lazy as _


class Enquiry(models.Model):
    project_name = models.CharField(_("project name"), max_length=200)
    existing_client = models.ForeignKey(
        "crm.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enquiries",
        verbose_name=_("existing client"),
    )
    new_client_name = models.CharField(
        _("new client name"),
        max_length=200,
        blank=True,
    )
    project_description = models.TextField(_("project description"), blank=True)
    location = models.CharField(_("location"), max_length=200, blank=True)
    attachment = models.FileField(
        _("attachment"),
        upload_to="crm/enquiries/",
        blank=True,
    )

    def __str__(self):
        return self.project_name
