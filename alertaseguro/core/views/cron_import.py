from django.http import JsonResponse
from django.conf import settings
from core.services.api_importer import fetch_all_apis 
from core.services.ipma_service import update_ipma_warnings

CRON_TOKEN = "cron_token_@l3rt4s3gur0"

def cron_import(request):
    token = request.GET.get("token")
    if token != CRON_TOKEN:
        return JsonResponse({"error": "Token inválido"}, status=403)

    fetch_all_apis()
    update_ipma_warnings()

    return JsonResponse({"status": "ok"})