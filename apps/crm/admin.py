from django.contrib import admin

from .models import LeadManagement, Customer, Enquiry


@admin.register(LeadManagement)
class LeadManagementAdmin(admin.ModelAdmin):
    list_display = ("contact_name", "company", "email_address", "phone", "lead_source")
    search_fields = ("contact_name", "company", "email_address", "phone", "lead_source")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "email_address", "company_name", "phone_number")
    search_fields = ("customer_name", "email_address", "company_name", "phone_number")


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("project_name", "existing_client", "new_client_name", "location")
    search_fields = ("project_name", "new_client_name", "location")
    list_filter = ("existing_client",)
