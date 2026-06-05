"""
Signals for the Projects app.

BOQ → Project auto-creation
────────────────────────────
When a ``Boq`` record is saved with ``is_approved=True`` and no linked Project
already exists, this signal automatically creates a Job Order (Project) seeded
with data from the BOQ's associated Enquiry.

The signal is connected inside ``ProjectsConfig.ready()`` so it is registered
exactly once when Django starts, regardless of which code path saves the BOQ.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _get_unlinked_quote(boq):
    """
    Return the first Quote attached to this BOQ that does not yet have a
    linked Project (OneToOne ``project`` reverse accessor), or ``None``.
    """
    from apps.assessment.models import Quote  # lazy import – avoids circular refs

    for quote in Quote.objects.filter(boq=boq).select_related("boq"):
        # The OneToOne is defined on Project.quote; if no Project references
        # this quote the reverse accessor raises RelatedObjectDoesNotExist.
        try:
            _ = quote.project  # already linked
        except Exception:
            return quote  # free to attach
    return None


@receiver(post_save, sender="assessment.Boq")
def auto_create_project_on_boq_approval(sender, instance, created, **kwargs):
    """
    ``post_save`` handler for ``assessment.Boq``.

    Fires on every save; skips cheaply unless the BOQ has just become approved
    and no Project is linked to it yet.
    """
    # Only act when the BOQ is approved
    if not instance.is_approved:
        return

    # Lazy import to avoid circular dependencies at module load time
    from apps.Projects.models.project import Project

    # Idempotency guard – do nothing if a Project already exists for this BOQ
    if Project.objects.filter(boq=instance).exists():
        return

    # ── Derive fields from the linked Enquiry (if present) ────────────────
    enquiry = instance.enquiry  # may be None

    project_name = (
        enquiry.project_name
        if enquiry
        else f"Project for {instance.boq_number}"
    )
    description = enquiry.project_description if enquiry else ""
    location = enquiry.location if enquiry else ""

    # ── Resolve client ─────────────────────────────────────────
    from apps.Projects.services.project_service import _resolve_or_create_client
    client = _resolve_or_create_client(enquiry,getattr(instance, "approved_by", None))

    # Link the first available unlinked Quote on this BOQ (optional)
    quote = _get_unlinked_quote(instance)

    # ── Create the Job Order ───────────────────────────────────────────────
    try:
        project = Project.objects.create(
            boq=instance,
            quote=quote,
            client=client,
            project_name=project_name,
            description=description,
            location=location,
            status="quotation_approved",
            created_by=getattr(instance, "approved_by", None)
        )
        logger.info(
            "[Projects] Auto-created Project %s (%s) from BOQ %s (%s).",
            project.job_number,
            project.id,
            instance.boq_number,
            instance.id,
        )
    except Exception:
        logger.exception(
            "[Projects] Failed to auto-create Project for BOQ %s (%s).",
            instance.boq_number,
            instance.id,
        )
