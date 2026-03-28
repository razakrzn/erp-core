from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Boq, Quote, QuoteItem, QuoteTermsConditions
from apps.settings.models import TermsConditions


@receiver(post_save, sender=Boq)
def create_quote_when_boq_approved(sender, instance, **kwargs):
    if not instance.is_approved or instance.is_rejected:
        if instance.quotes.exists():
            instance.quotes.all().delete()
        return
    if instance.quotes.exists():
        return
    quote = Quote.objects.create(
        boq=instance,
        created_by=instance.updated_by or instance.created_by,
        updated_by=instance.updated_by or instance.created_by,
    )

    # Automatically add default terms and conditions from settings module
    default_terms = TermsConditions.objects.filter(is_default=True)
    for term in default_terms:
        QuoteTermsConditions.objects.create(
            quote=quote,
            title=term.title,
            content=term.content,
            category=term.category
        )


@receiver(post_save, sender=QuoteItem)
def refresh_quote_totals_on_item_save(sender, instance, **kwargs):
    if instance.quote:
        instance.quote.refresh_totals()


@receiver(post_delete, sender=QuoteItem)
def refresh_quote_totals_on_item_delete(sender, instance, **kwargs):
    if instance.quote:
        instance.quote.refresh_totals()
