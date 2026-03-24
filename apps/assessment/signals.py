from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Boq, Quote, QuoteItem


@receiver(post_save, sender=Boq)
def create_quote_when_boq_approved(sender, instance, **kwargs):
    if not instance.is_approved or instance.is_rejected:
        if instance.quotes.exists():
            instance.quotes.all().delete()
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
