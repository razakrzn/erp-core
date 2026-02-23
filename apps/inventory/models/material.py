# inventory/models/material.py

from django.db import models

from .base import BaseMasterModel


class Material(BaseMasterModel):
    description = models.TextField(blank=True, null=True)

    class Meta(BaseMasterModel.Meta):
        db_table = "inv_materials"

    def __str__(self):
        return self.name
