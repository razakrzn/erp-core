"""
Signals for the navigation app.

- Module post_save: when a new Module is created, automatically create the four
  default CRUD permissions ({feature_code}.{module_code}.create|view|edit|delete).
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.navigation.models import Module
from apps.navigation.services.permission_generator import generate_default_permissions_for_module


@receiver(post_save, sender=Module)
def on_module_created_create_default_permissions(sender, instance: Module, created: bool, **kwargs) -> None:
    """Create default create/view/edit/delete permissions when a new Module is saved."""
    if created:
        generate_default_permissions_for_module(instance)
