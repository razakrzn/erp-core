from django.apps import AppConfig


class NavigationConfig(AppConfig):
    name = "apps.navigation"

    def ready(self) -> None:
        import apps.navigation.signals  # noqa: F401
