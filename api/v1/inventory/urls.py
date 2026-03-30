from rest_framework.routers import DefaultRouter

from .views import (
    BrandViewSet,
    CategoryViewSet,
    FinishViewSet,
    GradeViewSet,
    MaterialViewSet,
    ProductViewSet,
    SizeViewSet,
    ThicknessViewSet,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="inventory-category")
router.register(r"brands", BrandViewSet, basename="inventory-brand")
router.register(r"materials", MaterialViewSet, basename="inventory-material")
router.register(r"sizes", SizeViewSet, basename="inventory-size")
router.register(r"thickness", ThicknessViewSet, basename="inventory-thickness")
router.register(r"grades", GradeViewSet, basename="inventory-grade")
router.register(r"finishes", FinishViewSet, basename="inventory-finish")
router.register(r"products", ProductViewSet, basename="inventory-product")

urlpatterns = router.urls
