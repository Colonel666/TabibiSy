from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tabibi_models.models import User, Token


class TokenInline(admin.StackedInline):
    model = Token

    def has_add_permission   (self, request, obj     ): return False
    # def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False

@admin.register(User)
class MyUserAdmin(UserAdmin):
    inlines = [TokenInline, ]
    list_display = ['email', 'id', 'user_type', 'first_name', 'last_name']
    fieldsets = (
        (None             , {'fields': ('password', )}),
        ('Personal info'  , {'fields': ('first_name', 'last_name', 'email', )}),
        ('Permissions'    , {'fields': ('is_active', 'is_superuser', )}),
        ('Important dates', {'fields': ('last_login', )}),
        ('My fields'      , {'fields': ('email_verified', 'created_at', 'updated_at', 'user_type', 'id_scan', 'id_number', 'user_approved', )}))
    add_fieldsets = (
        (None             , {'fields': ('email', 'password1', 'password2'), 'classes': ('wide',)}),)

    ordering = ('-created_at', )
    readonly_fields = ['created_at', 'updated_at']
    list_filter = ('is_superuser', 'is_active', 'user_type', )
    list_per_page = 300
