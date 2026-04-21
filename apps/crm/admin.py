from django.contrib import admin

from .models import Customer, Enquiry


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "email_address", "company_name", "phone_number")
    search_fields = ("customer_name", "email_address", "company_name", "phone_number")


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("project_name", "existing_client", "new_client_name", "location")
    search_fields = ("project_name", "new_client_name", "location")
    list_filter = ("existing_client",)
