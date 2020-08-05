from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account
# Register your models here.


class AccountAdmin(UserAdmin):
    list_display = ('name', 'phoneNumber', 'email', 'is_admin', 'is_staff', 'is_active')
    search_fields = ('name', 'phoneNumber', 'email')
    readonly_fields = ()
    ordering = ('name',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account, AccountAdmin)