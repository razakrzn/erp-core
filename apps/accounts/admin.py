from django.contrib import admin

from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('is_staff',)
