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
        next_run_time=timezone.now(), 
    )

    scheduler.add_job(
        update_ipma_warnings,
        "interval",
        minutes=20,
        id="update_ipma_20min",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        next_run_time=timezone.now(),
    )

    scheduler.start()