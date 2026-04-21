from rest_framework.routers import DefaultRouter

from .views import CustomerViewSet, EnquiryViewSet

router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename="crm-customer")
router.register(r"enquiries", EnquiryViewSet, basename="crm-enquiry")

urlpatterns = router.urls
