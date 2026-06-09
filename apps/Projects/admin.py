from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html

from apps.assessment.models import QuoteItem
from apps.inventory.models import Product

from .models import (
    Project,
    ProjectTeamMember,
    Milestone,
    Task,
    Material,
    Labour,
    Other,
    SiteLog,
    SiteLogPhoto,
    Timesheet,
    ProjectDocument,
    ProjectMaterial,
    QualityCheckpoint,
    DeliverySchedule,
    ReworkRequest,
    InstallationLog,
    DXFFile,
    DXFAnalysisResult,
)


class ProjectTeamMemberInline(admin.TabularInline):
    model = ProjectTeamMember
    extra = 1


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["job_number", "project_name", "status", "start_date", "end_date", "contract_value", "is_active"]
    list_filter = ["status", "is_active", "created_at"]
    search_fields = ["job_number", "project_name", "description", "location"]
    inlines = [ProjectTeamMemberInline, MilestoneInline, TaskInline]


@admin.register(ProjectTeamMember)
class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ["project", "employee", "designation", "role_in_project", "allocation_pct", "is_active"]
    list_filter = ["role_in_project", "is_active"]
    search_fields = ["project__job_number", "employee__first_name", "employee__last_name"]


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ["project", "name", "status", "due_date", "completion_percentage"]
    list_filter = ["status"]
    search_fields = ["project__job_number", "name"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["project", "title", "assigned_to", "priority", "status", "due_date"]
    list_filter = ["priority", "status"]
    search_fields = ["project__job_number", "title"]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["project", "item", "material", "unit", "req_qty", "stock_on_hand"]
    fields = ["project", "item", "material", "unit_ui", "stock_on_hand_ui", "req_qty", "notes_remarks"]
    readonly_fields = ["unit_ui", "stock_on_hand_ui"]
    search_fields = ["project__job_number", "item__name", "material__name", "material__sku", "material__product_code"]
    list_select_related = ["project", "item", "material"]
    autocomplete_fields = ["material"]

    class Media:
        js = ("Projects/admin/estimate_admin.js",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "quote-items/",
                self.admin_site.admin_view(self.quote_items_view),
                name="projects_material_quote_items",
            ),
            path(
                "product-stock/",
                self.admin_site.admin_view(self.product_stock_view),
                name="projects_material_product_stock",
            ),
        ]
        return custom_urls + urls

    def quote_items_view(self, request):
        project_id = request.GET.get("project_id")
        if not project_id:
            return JsonResponse({"items": []})

        items = QuoteItem.objects.filter(quote__project__id=project_id).order_by("name", "id")
        data = [{"id": item.id, "label": str(item)} for item in items]
        return JsonResponse({"items": data})

    def product_stock_view(self, request):
        product_id = request.GET.get("product_id")
        if not product_id:
            return JsonResponse({"stock_on_hand": "0", "unit": ""})

        product = (
            Product.objects.filter(id=product_id).select_related("unit").only("stock_on_hand", "unit__name").first()
        )
        if not product:
            return JsonResponse({"stock_on_hand": "0", "unit": ""})

        return JsonResponse(
            {
                "stock_on_hand": str(product.stock_on_hand or 0),
                "unit": str(product.unit) if product.unit else "",
            }
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "item":
            project_id = request.POST.get("project") or request.GET.get("project")
            if project_id:
                kwargs["queryset"] = QuoteItem.objects.filter(quote__project__id=project_id).order_by("name", "id")
            else:
                kwargs["queryset"] = QuoteItem.objects.none()
        elif db_field.name == "project":
            kwargs["queryset"] = Project.objects.order_by("job_number")
        elif db_field.name == "material":
            kwargs["queryset"] = Product.objects.order_by("name")

        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "project":
            formfield.widget.attrs["data-quote-items-url"] = reverse("admin:projects_material_quote_items")
        elif db_field.name == "material":
            formfield.widget.attrs["data-stock-url"] = reverse("admin:projects_material_product_stock")
        return formfield

    def stock_on_hand_ui(self, obj):
        return format_html('<span id="material-stock-value">{}</span>', obj.stock_on_hand if obj else "0")

    stock_on_hand_ui.short_description = "stock on hand"

    def unit_ui(self, obj):
        return format_html('<span id="material-unit-value">{}</span>', obj.unit if obj and obj.unit else "")

    unit_ui.short_description = "unit"


@admin.register(Labour)
class LabourAdmin(admin.ModelAdmin):
    list_display = ["project", "designation", "hrs", "rate", "amount"]
    list_filter = ["project"]
    search_fields = ["project__job_number", "designation__name"]
    readonly_fields = ["amount_ui"]
    fields = ["project", "designation", "hrs", "rate", "amount_ui"]

    class Media:
        js = ("Projects/admin/estimate_admin.js",)

    def amount_ui(self, obj):
        return format_html('<span id="labour-amount-value">{}</span>', obj.amount if obj else "0")

    amount_ui.short_description = "amount"


admin.site.register(SiteLog)
admin.site.register(SiteLogPhoto)
admin.site.register(Timesheet)
admin.site.register(ProjectDocument)
admin.site.register(ProjectMaterial)
admin.site.register(QualityCheckpoint)
admin.site.register(DeliverySchedule)
admin.site.register(ReworkRequest)
admin.site.register(InstallationLog)
admin.site.register(DXFFile)
admin.site.register(DXFAnalysisResult)
admin.site.register(Other)
