from .customer_serializers import CustomerSerializer
from .enquiry_serializers import EnquiryDetailSerializer, EnquiryListSerializer
from .leadmanagement_serializers import LeadManagementDetailSerializer, LeadManagementListSerializer

__all__ = [
    "CustomerSerializer",
    "EnquiryListSerializer",
    "EnquiryDetailSerializer",
    "LeadManagementListSerializer",
    "LeadManagementDetailSerializer",
]
