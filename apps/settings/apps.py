from django.apps import AppConfig


class SettingsConfig(AppConfig):
    name = "apps.settings"

    def ready(self):
        from . import signals  # noqa: F401
