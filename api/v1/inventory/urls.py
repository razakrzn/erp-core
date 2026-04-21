from rest_framework.routers import DefaultRouter

from .views import (
    BrandViewSet,
    CategoryViewSet,
    FinishViewSet,
    GradeViewSet,
    MaterialViewSet,
    ProductViewSet,
    PurchaseRequisitionLineItemViewSet,
    PurchaseRequisitionProductCategoryViewSet,
    PurchaseRequisitionProductNameViewSet,
    PurchaseRequisitionPreferredVendorNameViewSet,
    PurchaseRequisitionViewSet,
    SizeViewSet,
    ThicknessViewSet,
    UnitViewSet,
    VendorViewSet,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="inventory-category")
router.register(r"brands", BrandViewSet, basename="inventory-brand")
router.register(r"materials", MaterialViewSet, basename="inventory-material")
router.register(r"sizes", SizeViewSet, basename="inventory-size")
router.register(r"thicknesses", ThicknessViewSet, basename="inventory-thickness")
router.register(r"grades", GradeViewSet, basename="inventory-grade")
router.register(r"finishes", FinishViewSet, basename="inventory-finish")
router.register(r"units", UnitViewSet, basename="inventory-unit")
router.register(r"products", ProductViewSet, basename="inventory-product")
router.register(r"vendors", VendorViewSet, basename="inventory-vendor")
router.register(r"purchase-requisitions", PurchaseRequisitionViewSet, basename="inventory-purchase-requisition")
router.register(
    r"purchase-requisition-line-items",
    PurchaseRequisitionLineItemViewSet,
    basename="inventory-purchase-requisition-line-item",
)
router.register(
    r"purchase-requisition-product-names",
    PurchaseRequisitionProductNameViewSet,
    basename="inventory-purchase-requisition-product-name",
)
router.register(
    r"purchase-requisition-product-categories",
    PurchaseRequisitionProductCategoryViewSet,
    basename="inventory-purchase-requisition-product-category",
)
router.register(
    r"purchase-requisition-preferred-vendor-names",
    PurchaseRequisitionPreferredVendorNameViewSet,
    basename="inventory-purchase-requisition-preferred-vendor-name",
)

urlpatterns = router.urls
