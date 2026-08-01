"""
Django Admin Custom Registration
"""

from django.contrib import admin
from django_admin.models import DbUser, DbCustomer, DbAccount, DbTransaction


@admin.register(DbUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "is_active", "is_superuser", "created_at")
    search_fields = ("email",)
    list_filter = ("is_active", "is_superuser")


@admin.register(DbCustomer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "user", "created_at")
    search_fields = ("full_name", "phone")


@admin.register(DbAccount)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("id", "account_number", "account_type", "balance", "is_active", "created_at")
    search_fields = ("account_number",)
    list_filter = ("account_type", "is_active")


@admin.register(DbTransaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "transaction_type", "amount", "balance_after", "created_at")
    list_filter = ("transaction_type",)
    search_fields = ("account__account_number", "note")
