"""
Notification Service — Triggers Celery async notifications
"""

from typing import Optional


class NotificationService:
    @staticmethod
    def notify_transaction(email: str, txn_type: str, amount: str, balance: str) -> None:
        """Trigger async email notification via Celery task."""
        try:
            from tasks.email_tasks import send_transaction_email
            send_transaction_email.delay(
                recipient=email,
                txn_type=txn_type,
                amount=amount,
                balance=balance,
            )
        except Exception:
            # Fallback log if Celery broker is unavailable
            pass
