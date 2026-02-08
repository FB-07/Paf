import hashlib
import requests
from zoneinfo import ZoneInfo

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from core.models import Aviso


IPMA_URL = "https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json"
LISBON = ZoneInfo("Europe/Lisbon")


def make_api_id(item: dict) -> str:
    raw = (
        f"{item.get('idAreaAviso','')}|"
        f"{item.get('awarenessTypeName','')}|"
        f"{item.get('startTime','')}|"
        f"{item.get('endTime','')}|"
        f"{item.get('awarenessLevelID','')}"
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


class Command(BaseCommand):
    help = "Importa e atualiza avisos do IPMA"

    def handle(self, *args, **options):
        self.stdout.write("A obter avisos do IPMA...")

        try:
            response = requests.get(IPMA_URL, timeout=20)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro ao chamar a API do IPMA: {e}"))
            return

        criados = atualizados = ignorados = 0

        for item in data:
            inicio = parse_datetime(item.get("startTime"))
            fim = parse_datetime(item.get("endTime"))
            titulo = item.get("awarenessTypeName")
            descricao = item.get("text", "")
            area = item.get("idAreaAviso", "")
            gravidade = item.get("awarenessLevelID", "green")

            if not (inicio and fim and titulo):
                ignorados += 1
                continue

            if timezone.is_naive(inicio):
                inicio = timezone.make_aware(inicio, LISBON)
            if timezone.is_naive(fim):
                fim = timezone.make_aware(fim, LISBON)

            if gravidade not in {"green", "yellow", "orange", "red"}:
                gravidade = "green"

            api_id = make_api_id(item)

            _, criado = Aviso.objects.update_or_create(
                api_id=api_id,
                defaults={
                    "titulo": titulo,
                    "descricao": descricao,
                    "gravidade": gravidade,
                    "dataInicio": inicio,
                    "dataFim": fim,
                    "idAreaAviso": area,
                },
            )

            if criado:
                criados += 1
            else:
                atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído | Criados: {criados} | Atualizados: {atualizados} | Ignorados: {ignorados}"
            )
        )
