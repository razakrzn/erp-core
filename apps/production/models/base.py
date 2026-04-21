from django.db import models
from django.utils.text import slugify


class ProductionBaseModel(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def _generate_slug(self):
        base = slugify(self.name) or self.__class__.__name__.lower()
        candidate = base
        counter = 1
        while self.__class__.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
            counter += 1
            candidate = f"{base}-{counter}"
        return candidate

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_slug()
        super().save(*args, **kwargs)
