from django.contrib import admin

from .models import Company, CompanyFeature, CompanyModule


class CompanyFeatureInline(admin.TabularInline):
    model = CompanyFeature
    extra = 1


class CompanyModuleInline(admin.TabularInline):
    model = CompanyModule
    extra = 1


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "created_at")
    search_fields = ("name", "code")
    list_filter = ("is_active",)
    inlines = [CompanyFeatureInline, CompanyModuleInline]


@admin.register(CompanyFeature)
class CompanyFeatureAdmin(admin.ModelAdmin):
    list_display = ("company", "feature", "is_enabled")
    list_filter = ("is_enabled", "company", "feature")
    search_fields = (
        "company__name",
        "company__code",
        "feature__feature_name",
        "feature__feature_code",
    )


@admin.register(CompanyModule)
class CompanyModuleAdmin(admin.ModelAdmin):
    list_display = ("company", "module", "is_enabled")
    list_filter = ("is_enabled", "company", "module__feature")
    search_fields = (
        "company__name",
        "company__code",
        "module__module_name",
        "module__module_code",
        "module__feature__feature_name",
        "module__feature__feature_code",
    )
