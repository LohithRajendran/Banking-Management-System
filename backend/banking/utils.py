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
    2. Locks both accounts in consistent PK order to prevent deadlocks
    3. Re-validates balance on the locked, freshest DB records
    4. Deducts from sender and adds to receiver
    5. Creates a transaction record
    6. Invalidates cache for both users

    Uses Django's database transactions with SELECT FOR UPDATE to ensure:
    - Either ALL steps succeed
    - Or NONE of them happen (prevents partial transfers)
    - Concurrent transfers cannot bypass the balance check (race condition fix)

    Returns: (Transaction object, error_message or None)
    """
    from django.db import transaction as db_transaction
    from .models import BankAccount, Transaction

    # --- Pre-transaction validation ---
    if amount <= 0:
        return None, "Transfer amount must be greater than 0."

    if sender_account.pk == receiver_account.pk:
        return None, "You cannot transfer money to yourself."

    # --- Perform the transfer atomically with row-level locking ---
    # SELECT FOR UPDATE locks the rows so no other transaction can modify them
    # until this transaction completes. This prevents race conditions where two
    # concurrent transfers could both pass the balance check on stale data.
    #
    # We lock in ascending PK order to prevent deadlocks when two transactions
    # try to lock the same pair of accounts in opposite order at the same time.
    try:
        with db_transaction.atomic():
            # Lock both accounts in a consistent order (by primary key).
            # This is critical: if T1 locks A then B, and T2 locks B then A
            # simultaneously, they will deadlock. Always locking in PK order
            # prevents this.
            lock_ids = sorted([sender_account.pk, receiver_account.pk])
            locked_accounts = (
                BankAccount.objects
                .select_for_update()
                .filter(pk__in=lock_ids)
                .in_bulk()  # returns {pk: instance}
            )

            # Refresh our local references from the freshly locked DB rows
            locked_sender   = locked_accounts[sender_account.pk]
            locked_receiver = locked_accounts[receiver_account.pk]

            # Re-validate with fresh, locked data
            if not locked_sender.is_active:
                return None, "Your account is not active."

            if not locked_receiver.is_active:
                return None, "Recipient's account is not active."

            if locked_sender.balance < amount:
                return None, (
                    f"Insufficient balance. Your balance is ₹{locked_sender.balance}."
                )

            # Step 1: Deduct from sender
            locked_sender.balance -= amount
            locked_sender.save(update_fields=['balance'])

            # Step 2: Add to receiver
            locked_receiver.balance += amount
            locked_receiver.save(update_fields=['balance'])

            # Step 3: Create transaction record
            txn = Transaction.objects.create(
                sender=locked_sender,
                receiver=locked_receiver,
                amount=amount,
                transfer_type=transfer_type,
                status='completed',
                description=description,
            )

            # Step 4: Propagate new balance back to the caller's references
            # so views can return the updated balance without a second DB query.
            sender_account.balance   = locked_sender.balance
            receiver_account.balance = locked_receiver.balance

            # Step 5: Clear cached dashboard data for both users
            invalidate_user_cache(locked_sender.user.id)
            invalidate_user_cache(locked_receiver.user.id)

            logger.info(
                f"Transfer successful: {locked_sender.account_number} → "
                f"{locked_receiver.account_number} | ₹{amount} | {txn.reference_number}"
            )

            return txn, None  # Success!

    except Exception as e:
        logger.error(f"Transfer failed: {str(e)}")
        return None, "Transfer failed due to an internal error. Please try again."
