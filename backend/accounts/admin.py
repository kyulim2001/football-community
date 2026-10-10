from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Block, EmailVerification

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'username', 'email', 'nickname', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'nickname', 'email']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'nickname', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'nickname', 'password1', 'password2'),
        }),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'nickname']
    search_fields = ['user__username', 'nickname']

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['id', 'blocker', 'blocked', 'created_at']
    search_fields = ['blocker__username', 'blocked__username']
    list_filter = ['created_at']

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'code', 'created_at']
    search_fields = ['email']
    list_filter = ['created_at']
