from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Boq, BoqItem, Quote, QuoteItem


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


@receiver(post_save, sender=Boq)
def create_quote_when_boq_approved(sender, instance, **kwargs):
    if not instance.is_approved or instance.is_rejected:
        return
    if instance.quotes.exists():
        return
    Quote.objects.create(
        boq=instance,
        created_by=instance.updated_by or instance.created_by,
        updated_by=instance.updated_by or instance.created_by,
    )


@receiver(post_save, sender=QuoteItem)
def refresh_quote_totals_on_item_save(sender, instance, **kwargs):
    if instance.quote:
        instance.quote.refresh_totals()


@receiver(post_delete, sender=QuoteItem)
def refresh_quote_totals_on_item_delete(sender, instance, **kwargs):
    if instance.quote:
        instance.quote.refresh_totals()
