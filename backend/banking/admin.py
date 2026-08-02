"""
Django Admin — Register your models here so you can manage them
from the admin panel at http://localhost:8000/admin/

Create a superuser with: python manage.py createsuperuser
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, BankAccount, Transaction


# --- Custom User Admin ---
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Columns shown in the user list
    list_display = ('email', 'first_name', 'last_name', 'web_id', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'web_id')
    ordering = ('-date_joined',)

    # Fields shown when editing a user
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'web_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fields shown when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


# --- Bank Account Admin ---
@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'user', 'balance', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('account_number', 'user__email')
    readonly_fields = ('account_number', 'created_at')


# --- Transaction Admin ---
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'sender', 'receiver', 'amount', 'transfer_type', 'status', 'timestamp')
    list_filter = ('transfer_type', 'status')
    search_fields = ('reference_number', 'sender__account_number', 'receiver__account_number')
    readonly_fields = ('reference_number', 'timestamp')
    ordering = ('-timestamp',)
