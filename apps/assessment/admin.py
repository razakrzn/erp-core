from django.contrib import admin

from .models import Boq, BoqItem


class BoqItemInline(admin.TabularInline):
    model = BoqItem
    extra = 0


@admin.register(Boq)
class BoqAdmin(admin.ModelAdmin):
    list_display = ("boq_number", "enquiry", "enquiry_project_name", "updated_at")
    search_fields = ("boq_number", "enquiry__project_name")
    list_filter = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("boq_number", "enquiry", "is_approved", "is_rejected")}),
        (
            "Enquiry Details",
            {
                "fields": (
                    "enquiry_project_name",
                    "enquiry_status",
                    "enquiry_client_name",
                    "enquiry_attachment",
                )
            },
        ),
        ("Audit", {"fields": ("created_at", "updated_at")}),
    )
    inlines = [BoqItemInline]
    readonly_fields = (
        "enquiry_project_name",
        "enquiry_status",
        "enquiry_client_name",
        "enquiry_attachment",
        "created_at",
        "updated_at",
    )

    def enquiry_project_name(self, obj):
        return obj.enquiry.project_name if obj.enquiry else ""

    enquiry_project_name.short_description = "project name"

    def enquiry_status(self, obj):
        return obj.enquiry.boq_status if obj.enquiry else ""

    enquiry_status.short_description = "status"

    def enquiry_client_name(self, obj):
        if not obj.enquiry:
            return ""
        if obj.enquiry.existing_client:
            return obj.enquiry.existing_client.customer_name
        return obj.enquiry.new_client_name

    enquiry_client_name.short_description = "client"

    def enquiry_attachment(self, obj):
        if not obj.enquiry:
            return ""
        return obj.enquiry.attachment

    enquiry_attachment.short_description = "attachment"


@admin.register(BoqItem)
class BoqItemAdmin(admin.ModelAdmin):
    list_display = ("item_code", "name", "boq", "quantity", "unit", "is_template", "updated_at")
    search_fields = ("item_code", "name", "boq__boq_number")
    list_filter = ("is_template", "created_at", "updated_at")
