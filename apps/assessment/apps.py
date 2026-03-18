from django.apps import AppConfig


class AssessmentConfig(AppConfig):
    name = "apps.assessment"

    def ready(self):
        from . import signals  # noqa: F401
