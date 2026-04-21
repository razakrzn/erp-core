from django.contrib import admin

from .models import Feature, Module, Permission


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


class PermissionInline(admin.TabularInline):
    model = Permission
    extra = 1


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("feature_name", "feature_code", "order", "icon")
    search_fields = ("feature_name", "feature_code")
    list_filter = ("order",)
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("module_name", "module_code", "feature", "route", "order", "icon")
    search_fields = ("module_name", "module_code", "route", "feature__feature_name")
    list_filter = ("feature",)
    inlines = [PermissionInline]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("permission_code", "permission_name", "module")
    search_fields = ("permission_code", "permission_name", "module__module_name")
    list_filter = ("module",)
