from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.signals
        from django.core.management import call_command
        try:
            call_command("ipma_avisos")
        except Exception:
            pass
