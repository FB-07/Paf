from django.apps import AppConfig
import threading
import os

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return

        from core.services.api_importer import fetch_all_apis
        from core.services.ipma_service import update_ipma_warnings

        def run_startup_tasks():
            print("Atualizando Ocorrencias...")
            fetch_all_apis()
            print("Ocorrencias atualizados.")

            print("Atualizando avisos IPMA...")
            update_ipma_warnings()
            print("Avisos IPMA atualizados.")

            print("Startup fetch completo")

        threading.Thread(target=run_startup_tasks).start()