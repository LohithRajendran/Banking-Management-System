"""
Async Email Notification Tasks
"""

import logging
from tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.email_tasks.send_transaction_email")
def send_transaction_email(recipient: str, txn_type: str, amount: str, balance: str):
    """Simulates sending an email receipt asynchronously."""
    logger.info(
        f"[EMAIL SENT] To: {recipient} | Type: {txn_type} | Amount: ${amount} | New Balance: ${balance}"
    )
    return True
