"""
Celery Application Instance & Schedule Configuration
"""

from celery import Celery
from celery.schedules import crontab
from config.settings_fastapi import settings

celery_app = Celery(
    "banking_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.email_tasks",
        "tasks.report_tasks",
        "tasks.interest_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Celery Beat Periodic Schedule
celery_app.conf.beat_schedule = {
    "apply-daily-savings-interest": {
        "task": "tasks.interest_tasks.apply_daily_interest",
        "schedule": crontab(hour=0, minute=0),  # midnight daily
    },
    "generate-monthly-statements": {
        "task": "tasks.report_tasks.generate_monthly_statements",
        "schedule": crontab(0, 0, day_of_month="1"),  # 1st of every month
    },
}
