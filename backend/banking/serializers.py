"""
Banking App — Serializers
============================
Serializers convert between Python objects (from the database) and JSON (for the API).

Think of a serializer like a translator:
  Database Object  →  [Serializer]  →  JSON (sent to React)
  JSON from React  →  [Serializer]  →  Python object (saved to database)

Each serializer is like a form that says "what fields are we reading/writing".
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, BankAccount, Transaction


# ============================================
# USER SERIALIZERS
# ============================================

class UserSignupSerializer(serializers.ModelSerializer):
    """
    Used for the signup form.
    Takes: first_name, last_name, email, password, confirm_password
    Creates a new user account.
    """

    # confirm_password is write-only (not stored, just for validation)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password', 'confirm_password')
        extra_kwargs = {
            'password': {'write_only': True},  # Never include password in API responses!
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        """Check that the email is not already registered."""
        if CustomUser.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate(self, data):
        """Check that passwords match."""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        # Use Django's built-in password strength validation
        validate_password(data['password'])
        return data

    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        # Remove confirm_password — we don't store it
        validated_data.pop('confirm_password')

        # Use email as username too (Django needs a username field)
        user = CustomUser.objects.create_user(
            username=validated_data['email'],  # Use email as username
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],  # create_user() hashes the password
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Used to return basic user info in API responses.
    Read-only — does not accept any input.
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 'web_id', 'date_joined')
        read_only_fields = fields  # Everything is read-only

    def get_full_name(self, obj):
        """Return the user's full name."""
        return obj.get_full_name()


# ============================================
# BANK ACCOUNT SERIALIZERS
# ============================================

class BankAccountSerializer(serializers.ModelSerializer):
    """
    Returns bank account info including the account owner's details.
    """
    owner_name = serializers.SerializerMethodField()
    owner_email = serializers.SerializerMethodField()
    owner_web_id = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = (
            'id',
            'account_number',
            'balance',
            'is_active',
            'created_at',
            'owner_name',
            'owner_email',
            'owner_web_id',
        )
        read_only_fields = fields

    def get_owner_name(self, obj):
        return obj.user.get_full_name()

    def get_owner_email(self, obj):
        return obj.user.email

    def get_owner_web_id(self, obj):
        return obj.user.web_id


# ============================================
# TRANSACTION SERIALIZERS
# ============================================

class TransactionSerializer(serializers.ModelSerializer):
    """
    Returns transaction details with human-readable sender/receiver info.
    """
    sender_account = serializers.SerializerMethodField()
    sender_name = serializers.SerializerMethodField()
    receiver_account = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = (
            'id',
            'reference_number',
            'amount',
            'transfer_type',
            'status',
            'description',
            'timestamp',
            'sender_account',
            'sender_name',
            'receiver_account',
            'receiver_name',
        )
        read_only_fields = fields

    def get_sender_account(self, obj):
        return obj.sender.account_number if obj.sender else 'Deleted Account'

    def get_sender_name(self, obj):
        return obj.sender.user.get_full_name() if obj.sender else 'Deleted User'

    def get_receiver_account(self, obj):
        return obj.receiver.account_number if obj.receiver else 'Deleted Account'

    def get_receiver_name(self, obj):
        return obj.receiver.user.get_full_name() if obj.receiver else 'Deleted User'


# ============================================
# TRANSFER SERIALIZERS
# ============================================

class BankTransferSerializer(serializers.Serializer):
    """
    Input data for a Bank Transfer (using account number).
    This is NOT a ModelSerializer — it doesn't map to a database table.
    It just validates the input data.
    """
    recipient_account_number = serializers.CharField(
        max_length=12,
        min_length=12,
        help_text="12-digit account number of the recipient."
    )
    amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        min_value=1,
        help_text="Amount to transfer. Must be at least 1."
    )
    description = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default='',
        help_text="Optional note/description."
    )

    def validate_recipient_account_number(self, value):
        """Ensure the account number contains only digits."""
        if not value.isdigit():
            raise serializers.ValidationError("Account number must contain only digits.")
        return value


class WebIDTransferSerializer(serializers.Serializer):
    """
    Input data for a Web ID Transfer (using Web ID).
    """
    recipient_web_id = serializers.CharField(
        max_length=20,
        help_text="Web ID of the recipient (e.g., john1abc)."
    )
    amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        min_value=1,
        help_text="Amount to transfer. Must be at least 1."
    )
    description = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default='',
        help_text="Optional note/description."
    )
