"""
Django ORM models referencing existing database tables for Django Admin interface.
managed = False tells Django not to create/alter these tables (managed by Alembic).
"""

from django.db import models


class DbUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    hashed_password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email


class DbCustomer(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(DbUser, on_delete=models.CASCADE, db_column="user_id")
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=500, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "customers"
        verbose_name = "Customer Profile"

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


class DbAccount(models.Model):
    ACCOUNT_TYPES = (
        ("SAVINGS", "Savings"),
        ("CURRENT", "Current"),
    )
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(DbCustomer, on_delete=models.CASCADE, db_column="customer_id")
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=14, decimal_places=2)
    min_balance = models.DecimalField(max_digits=14, decimal_places=2)
    overdraft_limit = models.DecimalField(max_digits=14, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "accounts"
        verbose_name = "Bank Account"

    def __str__(self):
        return f"{self.account_number} - {self.account_type} (${self.balance})"


class DbTransaction(models.Model):
    TRANSACTION_TYPES = (
        ("DEPOSIT", "Deposit"),
        ("WITHDRAWAL", "Withdrawal"),
        ("TRANSFER", "Transfer"),
        ("INTEREST", "Interest"),
    )
    id = models.BigAutoField(primary_key=True)
    account = models.ForeignKey(DbAccount, on_delete=models.CASCADE, db_column="account_id", related_name="txns")
    to_account = models.ForeignKey(DbAccount, on_delete=models.SET_NULL, null=True, db_column="to_account_id", related_name="recv_txns")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    balance_after = models.DecimalField(max_digits=14, decimal_places=2)
    note = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "transactions"
        verbose_name = "Transaction Ledger"

    def __str__(self):
        return f"{self.transaction_type}: ${self.amount} on Account {self.account_id}"
