from django.db import models
from django.contrib.auth.models import AbstractUser

from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ['-created_at']

    def __str__(self):
        return self.username
