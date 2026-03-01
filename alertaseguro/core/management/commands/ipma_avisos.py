from django.core.management.base import BaseCommand
from core.services.ipma_service import update_ipma_warnings


class Command(BaseCommand):
    help = "Importa e atualiza avisos do IPMA"

    def handle(self, *args, **options):
        self.stdout.write("A obter avisos do IPMA...")

        try:
            criados, atualizados, ignorados = update_ipma_warnings()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Concluído | Criados: {criados} | Atualizados: {atualizados} | Ignorados: {ignorados}"
                )
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro: {e}"))