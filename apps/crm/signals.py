from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.assessment.models import Boq
from .models import Enquiry

CONFIRMED_ENQUIRY_STATUS = "Confirmed"
CONFIRMED_ENQUIRY_STATUS_NORMALIZED = CONFIRMED_ENQUIRY_STATUS.lower()
PENDING_ENQUIRY_STATUS = "pending"
PENDING_ENQUIRY_STATUS_NORMALIZED = PENDING_ENQUIRY_STATUS.lower()


@receiver(pre_save, sender=Enquiry)
def mark_boq_creation_on_enquiry_confirmation(sender, instance, **kwargs):
    instance._should_create_boq = False
    instance._should_delete_boq = False
    if not instance.pk:
        return

    previous_status = sender.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
    if previous_status is None:
        return

    old_status = (previous_status or "").strip().lower()
    new_status = (instance.status or "").strip().lower()
    if (
        old_status != CONFIRMED_ENQUIRY_STATUS_NORMALIZED
        and new_status == CONFIRMED_ENQUIRY_STATUS_NORMALIZED
    ):
        instance._should_create_boq = True
    if old_status != PENDING_ENQUIRY_STATUS_NORMALIZED and new_status == PENDING_ENQUIRY_STATUS_NORMALIZED:
        instance._should_delete_boq = True


@receiver(post_save, sender=Enquiry)
def create_boq_for_enquiry(sender, instance, created, **kwargs):
    if getattr(instance, "_should_delete_boq", False):
        Boq.objects.filter(enquiry=instance).delete()
        sender.objects.filter(pk=instance.pk).update(status=PENDING_ENQUIRY_STATUS)
        return
    normalized_status = (instance.status or "").strip().lower()
    should_create_on_create = created and normalized_status == CONFIRMED_ENQUIRY_STATUS_NORMALIZED
    should_create_on_transition = getattr(instance, "_should_create_boq", False)
    should_backfill_missing_confirmed_boq = (
        normalized_status == CONFIRMED_ENQUIRY_STATUS_NORMALIZED
        and not Boq.objects.filter(enquiry=instance).exists()
    )

    if should_create_on_create or should_create_on_transition or should_backfill_missing_confirmed_boq:
        Boq.objects.get_or_create(enquiry=instance)
