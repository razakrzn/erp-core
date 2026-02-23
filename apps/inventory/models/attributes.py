# inventory/models/attributes.py

from django.db import models

from .base import BaseMasterModel


class Size(BaseMasterModel):
    value = models.CharField(max_length=100)

    class Meta(BaseMasterModel.Meta):
        db_table = "inv_sizes"

    def __str__(self):
        return f"{self.name} ({self.value})"


class Thickness(BaseMasterModel):
    value = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta(BaseMasterModel.Meta):
        db_table = "inv_thickness"

    def __str__(self):
        return f"{self.name} ({self.value})"


class Grade(BaseMasterModel):

    class Meta(BaseMasterModel.Meta):
        db_table = "inv_grades"

    def __str__(self):
        return self.name


class Finish(BaseMasterModel):

    class Meta(BaseMasterModel.Meta):
        db_table = "inv_finishes"

    def __str__(self):
        return self.name
