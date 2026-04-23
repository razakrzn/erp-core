from django.contrib import admin

from .models import Accessory, Boq, BoqItem, Finish, Quote, QuoteItem, QuoteTermsConditions, Template, TemplateFinish


class BoqItemInline(admin.TabularInline):
    model = BoqItem
    extra = 0


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 0
    show_change_link = True
    fields = (
        "boq_item",
        "name",
        "category",
        "quantity",
        "unit_price",
        "amount",
        "finish_details",
    )
    readonly_fields = ("amount", "finish_details")

    def finish_details(self, obj):
        if not obj or not obj.pk:
            return "-"
        finish_names = list(obj.finishes.values_list("finish_name", flat=True))
        if not finish_names:
            return "-"
        return ", ".join(finish_names)

    finish_details.short_description = "finishes"


class FinishInline(admin.TabularInline):
    model = Finish
    extra = 0


class AccessoryInline(admin.TabularInline):
    model = Accessory
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
        if not obj.enquiry:
            return ""
        return obj.enquiry.status

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


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("quote_number", "boq", "status", "is_approved", "is_rejected", "updated_at")
    search_fields = ("quote_number", "boq__boq_number", "status")
    list_filter = ("status", "is_approved", "is_rejected", "created_at", "updated_at")
    inlines = [QuoteItemInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "quote_number",
                    "boq",
                    "status",
                    "is_approved",
                    "is_rejected",
                )
            },
        ),
        (
            "BOQ Details",
            {
                "fields": (
                    "boq_number",
                    "boq_is_approved",
                    "boq_is_rejected",
                    "boq_enquiry_project_name",
                    "boq_enquiry_status",
                    "boq_enquiry_client_name",
                    "boq_enquiry_attachment",
                )
            },
        ),
        ("Audit", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = (
        "quote_number",
        "boq_number",
        "boq_is_approved",
        "boq_is_rejected",
        "boq_enquiry_project_name",
        "boq_enquiry_status",
        "boq_enquiry_client_name",
        "boq_enquiry_attachment",
        "created_at",
        "updated_at",
    )

    def boq_number(self, obj):
        return obj.boq.boq_number if obj.boq else ""

    boq_number.short_description = "boq number"

    def boq_is_approved(self, obj):
        return obj.boq.is_approved if obj.boq else False

    boq_is_approved.short_description = "boq approved"
    boq_is_approved.boolean = True

    def boq_is_rejected(self, obj):
        return obj.boq.is_rejected if obj.boq else False

    boq_is_rejected.short_description = "boq rejected"
    boq_is_rejected.boolean = True

    def boq_enquiry_project_name(self, obj):
        if not obj.boq or not obj.boq.enquiry:
            return ""
        return obj.boq.enquiry.project_name

    boq_enquiry_project_name.short_description = "project name"

    def boq_enquiry_status(self, obj):
        if not obj.boq or not obj.boq.enquiry:
            return ""
        return obj.boq.enquiry.status

    boq_enquiry_status.short_description = "enquiry status"

    def boq_enquiry_client_name(self, obj):
        if not obj.boq or not obj.boq.enquiry:
            return ""
        enquiry = obj.boq.enquiry
        if enquiry.existing_client:
            return enquiry.existing_client.customer_name
        return enquiry.new_client_name

    boq_enquiry_client_name.short_description = "client"

    def boq_enquiry_attachment(self, obj):
        if not obj.boq or not obj.boq.enquiry:
            return ""
        return obj.boq.enquiry.attachment

    boq_enquiry_attachment.short_description = "attachment"


@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
    list_display = ("name", "quote", "boq_item", "category", "quantity", "unit_price", "amount", "updated_at")
    search_fields = ("name", "quote__quote_number", "boq_item__item_code", "category")
    list_filter = ("category", "created_at", "updated_at")
    inlines = [FinishInline, AccessoryInline]


@admin.register(Finish)
class FinishAdmin(admin.ModelAdmin):
    list_display = ("finish_name", "finish_type", "material", "quantity", "unit_price", "total_price", "quote_item")
    search_fields = ("finish_name", "finish_type", "material", "quote_item__name", "quote_item__quote__quote_number")
    list_filter = ("finish_type", "material")


@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ("accessory_id", "accessory_name", "accessory_price", "accessory_qty", "quote_item")
    search_fields = ("accessory_id", "accessory_name", "quote_item__name", "quote_item__quote__quote_number")


@admin.register(QuoteTermsConditions)
class QuoteTermsConditionsAdmin(admin.ModelAdmin):
    list_display = ("title", "quote", "category")
    search_fields = ("title", "content", "category", "quote__quote_number")
    list_filter = ("category",)


class TemplateFinishInline(admin.TabularInline):
    model = TemplateFinish
    extra = 0


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "created_at", "updated_at")
    search_fields = ("name", "category")
    list_filter = ("category", "created_at", "updated_at")
    inlines = [TemplateFinishInline]
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    fieldsets = (
        (None, {"fields": ("name", "category")}),
        ("Audit", {"fields": ("created_at", "updated_at", "created_by", "updated_by")}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TemplateFinish)
class TemplateFinishAdmin(admin.ModelAdmin):
    list_display = ("finish_name", "finish_type", "material", "template", "unit_price", "unit")
    search_fields = ("finish_name", "finish_type", "material", "template__name")
    list_filter = ("finish_type", "material")
