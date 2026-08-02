"""
Banking App — Helper Utilities
================================
This file contains helper functions used across the banking app.
Think of these as "tools in a toolbox" that views can use.
"""
from django.core.cache import cache
import logging

# Logger — records errors to the console for debugging
logger = logging.getLogger(__name__)


def get_dashboard_data_cached(user, account):
    """
    Get dashboard data from cache (Redis) if available.
    If not in cache, fetch from database and store in cache.
    
    HOW CACHING WORKS:
    - First request: Data is fetched from database (slow)
    - Data is stored in Redis with a key like 'dashboard_user_5'
    - Next requests: Data is fetched from Redis (super fast!)
    - Cache expires after 60 seconds → fresh data from database
    
    This is called "cache-aside" or "lazy loading" pattern.
    """
    cache_key = f'dashboard_user_{user.id}'

    # Try to get from cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache HIT for user {user.id}")
        return cached_data

    # Not in cache — build the data from database
    logger.info(f"Cache MISS for user {user.id} — fetching from DB")

    data = {
        'user_id': user.id,
        'full_name': user.get_full_name(),
        'email': user.email,
        'web_id': user.web_id,
        'account_number': account.account_number,
        'balance': str(account.balance),  # Convert Decimal to string for JSON
        'is_active': account.is_active,
        'account_created': account.created_at.isoformat(),
    }

    # Store in cache for 60 seconds
    cache.set(cache_key, data, timeout=60)
    return data


def invalidate_user_cache(user_id):
    """
    Delete a user's cached dashboard data.
    
    Call this whenever a user's balance changes (after a transfer).
    This forces the next dashboard request to fetch fresh data from database.
    """
    cache_key = f'dashboard_user_{user_id}'
    cache.delete(cache_key)
    logger.info(f"Cache INVALIDATED for user {user_id}")


def perform_transfer(sender_account, receiver_account, amount, transfer_type, description=''):
    """
    Transfer money between two bank accounts.
    
    This function:
    1. Validates the amount
    2. Checks the sender has enough balance
    3. Deducts from sender
    4. Adds to receiver
    5. Creates a transaction record
    6. Invalidates cache for both users
    
    Uses Django's database transactions to ensure:
    - Either ALL steps succeed
    - Or NONE of them happen (to prevent partial transfers)
    
    Returns: (Transaction object, error_message or None)
    """
    from django.db import transaction as db_transaction
    from .models import Transaction

    # --- Validation ---
    if amount <= 0:
        return None, "Transfer amount must be greater than 0."

    if not sender_account.is_active:
        return None, "Your account is not active."

    if not receiver_account.is_active:
        return None, "Recipient's account is not active."

    if sender_account.balance < amount:
        return None, f"Insufficient balance. Your balance is ₹{sender_account.balance}."

    if sender_account == receiver_account:
        return None, "You cannot transfer money to yourself."

    # --- Perform the transfer atomically ---
    # 'atomic()' means: run all database operations as one unit.
    # If any step fails (e.g., database error), all changes are rolled back.
    try:
        with db_transaction.atomic():
            # Step 1: Deduct from sender
            sender_account.balance -= amount
            sender_account.save()

            # Step 2: Add to receiver
            receiver_account.balance += amount
            receiver_account.save()

            # Step 3: Create transaction record
            txn = Transaction.objects.create(
                sender=sender_account,
                receiver=receiver_account,
                amount=amount,
                transfer_type=transfer_type,
                status='completed',
                description=description,
            )

            # Step 4: Clear cached dashboard data for both users
            invalidate_user_cache(sender_account.user.id)
            invalidate_user_cache(receiver_account.user.id)

            logger.info(
                f"Transfer successful: {sender_account.account_number} → "
                f"{receiver_account.account_number} | ₹{amount} | {txn.reference_number}"
            )

            return txn, None  # Success!

    except Exception as e:
        logger.error(f"Transfer failed: {str(e)}")
        return None, "Transfer failed due to an internal error. Please try again."
