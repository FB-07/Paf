from django.http import JsonResponse
from django.conf import settings
from core.models import IncidenteAPI
from core.services.api_importer import fetch_all_apis 
from core.services.ipma_service import update_ipma_warnings

CRON_TOKEN = "cron_token_@l3rt4s3gur0"

def cron_import(request):
    print("CRON EXECUTADO")

    token = request.GET.get("token")
    if token != CRON_TOKEN:
        return JsonResponse({"error": "Token inválido"}, status=403)

    before = IncidenteAPI.objects.count()
    fetch_all_apis()
    update_ipma_warnings()
    after = IncidenteAPI.objects.count()

    return JsonResponse({
        "before": before,
        "after": after,
        "status": "ok"
    })