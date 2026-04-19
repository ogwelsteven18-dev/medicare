from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'email', 'role', 'phone', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone', 'profile_pic', 'is_approved')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone', 'first_name', 'last_name', 'email')}),
    )
