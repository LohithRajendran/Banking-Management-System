"""
Banking App — Database Models
================================
Models are Python classes that represent database tables.
Each class = one table. Each attribute = one column in the table.

Django automatically creates the SQL tables when you run:
  python manage.py makemigrations
  python manage.py migrate

OUR TABLES:
  1. CustomUser     → Stores user accounts (email, name, web_id)
  2. BankAccount    → Stores bank accounts (account_number, balance)
  3. Transaction    → Stores every money transfer
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string


# ============================================
# HELPER FUNCTIONS — Generate unique IDs
# ============================================

def generate_account_number():
    """
    Creates a random 12-digit bank account number.
    Example: '481927364850'
    """
    return ''.join(random.choices(string.digits, k=12))


def generate_web_id():
    """
    Creates a unique 8-character Web ID for easy transfers.
    Like a UPI ID or PayPal handle.
    Example: 'john1abc'
    The format is: first 4 letters of name + 4 random digits
    """
    return ''.join(random.choices(string.ascii_lowercase, k=4)) + \
           ''.join(random.choices(string.digits, k=4))


def generate_reference_number():
    """
    Creates a unique transaction reference number.
    Example: 'TXN481927364850'
    """
    return 'TXN' + ''.join(random.choices(string.digits, k=12))


# ============================================
# TABLE 1: CUSTOM USER
# ============================================
class CustomUser(AbstractUser):
    """
    Our custom user model.
    
    We extend Django's built-in User model (AbstractUser) to add:
    - email login (instead of username login)
    - web_id (for Web ID transfers, like UPI)
    
    Django's AbstractUser already gives us:
    - first_name, last_name
    - password (stored securely as a hash)
    - is_active, is_staff, is_superuser
    - date_joined, last_login
    """

    # Override email to make it unique (Django's default allows duplicate emails!)
    email = models.EmailField(
        unique=True,
        help_text="User's email address. Used for login."
    )

    # Web ID — unique short identifier for Web ID transfers
    # blank=True means it's optional in forms (we auto-generate it)
    web_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Unique short ID for Web ID transfers. Auto-generated."
    )

    # Tell Django to use EMAIL as the login field instead of USERNAME
    USERNAME_FIELD = 'email'

    # Fields required when creating a user via command line
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        """
        Override save() to auto-generate a web_id if not already set.
        This runs every time we create or update a user.
        """
        if not self.web_id:
            # Keep trying until we get a unique web_id
            while True:
                candidate = generate_web_id()
                if not CustomUser.objects.filter(web_id=candidate).exists():
                    self.web_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        """How this user appears in the admin panel."""
        return f"{self.get_full_name()} ({self.email})"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


# ============================================
# TABLE 2: BANK ACCOUNT
# ============================================
class BankAccount(models.Model):
    """
    Stores a user's bank account details.
    
    One user can only have ONE bank account (OneToOneField).
    
    Think of this like a savings account with:
    - A unique account number
    - A current balance
    """

    # Link to the user — if the user is deleted, their account is deleted too
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='bank_account',
        help_text="The owner of this bank account."
    )

    # 12-digit account number — auto-generated, never editable
    account_number = models.CharField(
        max_length=12,
        unique=True,
        blank=True,   # We auto-generate this, so it's not required in forms
        help_text="Unique 12-digit account number."
    )

    # Balance — max 12 digits total, 2 decimal places
    # Example: 999999999999.99 (max balance)
    balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=1000.00,  # New accounts start with ₹1000 bonus!
        help_text="Current account balance."
    )

    # Whether this account is active
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive accounts cannot send or receive money."
    )

    # When this account was created
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Auto-generate a unique account number on first save."""
        if not self.account_number:
            while True:
                candidate = generate_account_number()
                if not BankAccount.objects.filter(account_number=candidate).exists():
                    self.account_number = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Account {self.account_number} — {self.user.get_full_name()}"

    class Meta:
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'


# ============================================
# TABLE 3: TRANSACTION
# ============================================
class Transaction(models.Model):
    """
    Records every money transfer in the system.
    
    Every time money moves from Account A to Account B,
    one Transaction record is created.
    """

    # --- Transfer Type Choices ---
    TRANSFER_TYPES = [
        ('bank', 'Bank Transfer'),     # Sent using account number
        ('webid', 'Web ID Transfer'),  # Sent using Web ID
    ]

    # --- Status Choices ---
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    # The account sending money
    # SET_NULL means: if sender's account is deleted, keep the transaction record (with null sender)
    sender = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_transactions',
        help_text="The account that sent the money."
    )

    # The account receiving money
    receiver = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_transactions',
        help_text="The account that received the money."
    )

    # How much money was transferred
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Amount transferred."
    )

    # Was this a bank transfer or web ID transfer?
    transfer_type = models.CharField(
        max_length=10,
        choices=TRANSFER_TYPES,
        help_text="Method used for this transfer."
    )

    # Did the transfer succeed?
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='completed',
    )

    # Optional note from the sender
    description = models.TextField(
        blank=True,
        help_text="Optional note/description for this transfer."
    )

    # Auto-generated unique reference number (like a receipt number)
    reference_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    # When did this transaction happen?
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Auto-generate a unique reference number on first save."""
        if not self.reference_number:
            while True:
                candidate = generate_reference_number()
                if not Transaction.objects.filter(reference_number=candidate).exists():
                    self.reference_number = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_number} | ₹{self.amount} | {self.transfer_type}"

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-timestamp']  # Newest transactions first
