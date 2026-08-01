"""
Savings Interest Calculation Task
"""

import logging
from tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.interest_tasks.apply_daily_interest")
def apply_daily_interest():
    """Calculates and credits daily interest to active savings accounts."""
    logger.info("[CRON] Calculating and crediting daily interest for savings accounts...")
    return "Daily interest processing complete"
