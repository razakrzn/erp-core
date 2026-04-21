try:
    from .celery import app as celery_app
except ModuleNotFoundError:  # pragma: no cover - optional before dependencies are installed
    celery_app = None

__all__ = ("celery_app",)
