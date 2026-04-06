from django.db import models
from django.utils.translation import gettext_lazy as _


class InventoryLookupModel(models.Model):
    name = models.CharField(_("name"), max_length=255, unique=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Category(InventoryLookupModel):
    class Meta(InventoryLookupModel.Meta):
        verbose_name = _("category")
        verbose_name_plural = _("categories")


class Brand(InventoryLookupModel):
    class Meta(InventoryLookupModel.Meta):
        verbose_name = _("brand")
        verbose_name_plural = _("brands")


class Material(InventoryLookupModel):
    class Meta(InventoryLookupModel.Meta):
        verbose_name = _("material")
        verbose_name_plural = _("materials")


class Size(InventoryLookupModel):
    class Meta(InventoryLookupModel.Meta):
        verbose_name = _("size")
        verbose_name_plural = _("sizes")


class Thickness(InventoryLookupModel):
    class Meta(InventoryLookupModel.Meta):
        verbose_name = _("thickness")
        verbose_name_plural = _("thicknesses")


class Grade(InventoryLookupModel):
    class Meta(InventoryLookupModel.Meta):
        verbose_name = _("grade")
        verbose_name_plural = _("grades")


class Finish(InventoryLookupModel):
    class Meta(InventoryLookupModel.Meta):
        verbose_name = _("finish")
        verbose_name_plural = _("finishes")


class Unit(InventoryLookupModel):
    class Meta(InventoryLookupModel.Meta):
        verbose_name = _("unit")
        verbose_name_plural = _("units")


class Product(models.Model):
    name = models.CharField(_("name"), max_length=255)
    sku = models.CharField(_("SKU"), max_length=100)
    product_code = models.CharField(_("product code"), max_length=100, unique=True, blank=True, null=True)
    status = models.CharField(_("status"), max_length=20, blank=True, null=True)
    price = models.DecimalField(_("price"), max_digits=12, decimal_places=2, default=0)
    standard_cost = models.DecimalField(
        _("standard cost"), max_digits=12, decimal_places=2, default=0, blank=True, null=True
    )
    reorder_level = models.PositiveIntegerField(_("reorder level"), default=0, blank=True, null=True)
    preferred_supplier = models.ForeignKey(
        "Vendor",
        verbose_name=_("preferred supplier"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    lead_time_days = models.PositiveIntegerField(_("lead time (days)"), default=0, blank=True, null=True)
    max_stock_level = models.PositiveIntegerField(_("max stock level"), blank=True, null=True)
    moq = models.PositiveIntegerField(_("MOQ (min order)"), default=1, blank=True, null=True)
    opening_stock = models.PositiveIntegerField(_("opening stock"), default=0, blank=True, null=True)
    opening_stock_date = models.DateField(_("opening stock date"), blank=True, null=True)
    hsn_sac_code = models.CharField(_("HSN / SAC code"), max_length=50, blank=True, null=True)
    admin_notes = models.TextField(_("administrative notes"), blank=True, null=True)
    category = models.ForeignKey(
        Category,
        verbose_name=_("category"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    brand = models.ForeignKey(
        Brand,
        verbose_name=_("brand"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    material = models.ForeignKey(
        Material,
        verbose_name=_("material"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    size = models.ForeignKey(
        Size,
        verbose_name=_("size"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    thickness = models.ForeignKey(
        Thickness,
        verbose_name=_("thickness"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    grade = models.ForeignKey(
        Grade,
        verbose_name=_("grade"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    finish = models.ForeignKey(
        Finish,
        verbose_name=_("finish"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    unit = models.ForeignKey(
        Unit,
        verbose_name=_("unit"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"
