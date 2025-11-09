from core.constants import Const
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tabibi_models.models import User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ['email', 'id', 'user_type', 'first_name', 'last_name']
    fieldsets = (
        (None             , {'fields': ('password', )}),
        ('Personal info'  , {'fields': ('first_name', 'last_name', 'email', )}),
        ('Permissions'    , {'fields': ('is_active', 'is_superuser', )}),
        ('Important dates', {'fields': ('last_login', )}),
        ('My fields'      , {'fields': ('email_verified', 'created_at', 'updated_at', 'user_type', )}))
    add_fieldsets = (
        (None             , {'fields': ('email', 'password1', 'password2'), 'classes': ('wide',)}),)

    ordering = ('-created_at', )
    readonly_fields = ['created_at', 'updated_at']
    list_filter = ('is_superuser', 'is_active', 'user_type', )
    list_per_page = 300
