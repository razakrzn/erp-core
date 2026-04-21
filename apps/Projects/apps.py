from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    name = "apps.Projects"

    def ready(self):
        from . import signals  # noqa: F401
