from django.http import JsonResponse
from django.conf import settings
from core.models import IncidenteAPI
from core.services.api_importer import fetch_all_apis
from core.services.ipma_service import update_ipma_warnings

def cron_import(request):
    print("CRON EXECUTADO")

    token = request.GET.get("token")

    if token != settings.CRON_TOKEN:
        return JsonResponse({"error": "Token inválido"}, status=403)

    try:
        before = IncidenteAPI.objects.count()

        print("A chamar fetch_all_apis")
        fetch_all_apis()

        print("A chamar update_ipma_warnings")
        update_ipma_warnings()

        after = IncidenteAPI.objects.count()
        
        print("Chamada completa")
        
        return JsonResponse({
            "before": before,
            "after": after,
            "status": "ok"
        })

    except Exception as e:
        print("ERRO NO CRON:", str(e))
        return JsonResponse({
            "error": str(e)
        }, status=500)