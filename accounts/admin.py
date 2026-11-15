from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import AppUserRegistrationForm
from .models import AppUser

@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    add_form = AppUserRegistrationForm
    list_display = ('username', 'email', 'registration_status', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('registration_status', 'is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email')
    ordering = ('username',)
    readonly_fields = ('last_login', 'date_joined')
    fieldsets = (
        ('Account', {"fields": ('username', 'email', 'password')}),
        ('Registration', {'fields': ('registration_status',)}),
        ('Access and permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        ('Create account', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')