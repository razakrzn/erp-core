"""
Signals for the navigation app.

- Module post_save: when a new Module is created, automatically create the four
  default CRUD permissions ({feature_code}.{module_code}.create|view|edit|delete).
"""

from contextlib import contextmanager
from contextvars import ContextVar

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.navigation.models import Module
from apps.navigation.services.permission_generator import generate_default_permissions_for_module


_skip_default_permission_generation: ContextVar[bool] = ContextVar(
    "skip_default_permission_generation",
    default=False,
)


@contextmanager
def suppress_default_permission_generation():
    """
    Temporarily disable automatic CRUD permission generation.

    Seeders can use this when they want to define a custom permission list in
    `ERP_STRUCTURE` and avoid the default create/view/edit/delete bundle.
    """

    token = _skip_default_permission_generation.set(True)
    try:
        yield
    finally:
        _skip_default_permission_generation.reset(token)


@receiver(post_save, sender=Module)
def on_module_created_create_default_permissions(sender, instance: Module, created: bool, **kwargs) -> None:
    """Create default create/view/edit/delete permissions when a new Module is saved."""
    if created and not _skip_default_permission_generation.get():
        generate_default_permissions_for_module(instance)
