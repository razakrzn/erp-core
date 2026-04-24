"""
Bootstrap helpers for Django settings without environment-variable configuration.
"""

from importlib import import_module

from django.conf import settings


def setup_django_settings() -> None:
    """
    Configure Django settings directly from `config.settings` if not configured yet.
    """
    if settings.configured:
        return

    settings_module = import_module("config.settings")
    configured_values = {
        name: getattr(settings_module, name) for name in dir(settings_module) if name.isupper()
    }
    settings.configure(**configured_values)
