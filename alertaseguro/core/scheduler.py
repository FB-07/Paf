from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from core.services.ipma_service import update_ipma_warnings

from core.services.api_importer import fetch_and_save


def start():
    scheduler = BackgroundScheduler(timezone=str(timezone.get_current_timezone()))

    scheduler.add_job(
        fetch_and_save,
        "interval",
        minutes=30,
        id="update_api_30min",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.add_job(update_ipma_warnings, "interval", minutes=10)

    scheduler.start()
