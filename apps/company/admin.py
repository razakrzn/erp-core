from django.contrib import admin

from .models import Company, CompanyFeature


class CompanyFeatureInline(admin.TabularInline):
    model = CompanyFeature
    extra = 1


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "created_at")
    search_fields = ("name", "code")
    list_filter = ("is_active",)
    inlines = [CompanyFeatureInline]


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