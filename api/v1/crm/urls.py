from rest_framework.routers import DefaultRouter

from .views import CustomerViewSet, EnquiryViewSet, LeadManagementViewSet

router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename="crm-customer")
router.register(r"enquiries", EnquiryViewSet, basename="crm-enquiry")
router.register(r"leads", LeadManagementViewSet, basename="crm-lead")

urlpatterns = router.urls
