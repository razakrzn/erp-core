from rest_framework.routers import DefaultRouter
from .views import EstimateLabourViewSet, EstimateMaterialViewSet, EstimateOtherViewSet, ProjectViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project-project")
router.register(r"estimate-materials", EstimateMaterialViewSet, basename="project-estimate-material")
router.register(r"estimate-labours", EstimateLabourViewSet, basename="project-estimate-labour")
router.register(r"estimate-others", EstimateOtherViewSet, basename="project-estimate-other")

urlpatterns = router.urls
