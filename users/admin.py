from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = [
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff'
    ]
    search_fields = [
        'email',
        'first_name',
        'last_name'
    ]
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'grade', 'profile_photo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2',  'is_staff', 'is_active')
        }),
    )


admin.site.register(CustomUser, UserAdmin)
