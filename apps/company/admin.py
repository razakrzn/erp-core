# admin.py
from django.contrib import admin
from .models import Company, CompanyUser

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('is_active',)

@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'is_owner', 'created_at')
    search_fields = ('user__username', 'company__name')
    list_filter = ('is_owner',)