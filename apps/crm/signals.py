from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.assessment.models import Boq
from .models import Enquiry


@receiver(post_save, sender=Enquiry)
def create_boq_for_enquiry(sender, instance, created, **kwargs):
    if not created:
        return
    Boq.objects.get_or_create(enquiry=instance)
