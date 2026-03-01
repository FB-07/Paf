from django.core.management.base import BaseCommand
from core.services.api_importer import fetch_all_apis

class Command(BaseCommand):
    help = "Atualiza todas as APIs: Incidentes, Hospitais, Bombeiros, Recursos Aéreos"

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando atualização das APIs...")
        fetch_all_apis()
        self.stdout.write(self.style.SUCCESS("Atualização completa!"))