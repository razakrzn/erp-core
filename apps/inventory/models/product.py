# inventory/models/product.py

import uuid

from django.db import models

from .category import Category
from .brand import Brand
from .material import Material
from .attributes import Size, Thickness, Grade, Finish


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)

    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    thickness = models.ForeignKey(Thickness, on_delete=models.SET_NULL, null=True, blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True)
    finish = models.ForeignKey(Finish, on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inv_products"
        ordering = ["name"]

    def _generate_sku(self):
        category_code = (self.category.code or "CAT").upper()
        brand_code = ((self.brand.code if self.brand else None) or "NOB").upper()
        if self.size:
            size_part = (self.size.code or self.size.value or self.size.name or "NOS")
        else:
            size_part = "NOS"
        size_code = str(size_part).replace(" ", "").replace("/", "").upper()
        random_code = str(uuid.uuid4()).split("-")[0].upper()
        return f"{category_code}-{brand_code}-{size_code}-{random_code}"

    def save(self, *args, **kwargs):
        if not self.sku:
            for _ in range(20):
                candidate = self._generate_sku()
                if not self.__class__.objects.filter(sku=candidate).exists():
                    self.sku = candidate
                    break
            if not self.sku:
                self.sku = self._generate_sku()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.sku}"
