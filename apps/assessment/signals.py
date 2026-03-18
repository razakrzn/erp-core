from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BoqItem


@receiver(post_save, sender=BoqItem)
def mark_enquiry_boq_approved(sender, instance, created, **kwargs):
    if not created:
        return
    boq = instance.boq
    if not boq or not boq.enquiry:
        return
    if not boq.is_approved and not boq.is_rejected:
        boq.is_approved = True
        boq.save(update_fields=["is_approved"])
    boq._sync_enquiry_status()
