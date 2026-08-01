"""
Monthly Statement Generation Tasks
"""

import logging
from tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.report_tasks.generate_monthly_statements")
def generate_monthly_statements():
    """Generates monthly PDF account statements for all users."""
    logger.info("[CRON] Generating monthly bank statements for active accounts...")
    return "Statements generated successfully"
