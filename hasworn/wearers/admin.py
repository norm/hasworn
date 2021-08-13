from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _

from .models import Wearer


class WearerAdmin(UserAdmin):
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'username',
                    'password',
                ),
            }
        ),
        (
            _('Personal info'),
            {
                'fields': (
                    'name',
                    'email',
                ),
            }
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            }
        ),
        (
            _('Important dates'),
            {
                'fields': (
                    'last_login',
                    'date_joined',
                ),
            }
        ),
    )
    list_display = (
        'username',
        'name',
        'email',
        'is_active',
        'is_staff',
        'is_superuser',
    )

admin.site.register(Wearer, WearerAdmin)
