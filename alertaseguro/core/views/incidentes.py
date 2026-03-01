from django.http import JsonResponse
from core.models import IncidenteAPI

def api_incidentes(request):
    incidentes = IncidenteAPI.objects.filter(latitude__isnull=False, longitude__isnull=False)
    data = list(incidentes.values(
        "api_id",
        "latitude",
        "longitude",
        "natureza",
        "category",
        "location_name",
        "parish",
        "county",
        "district",
        "status",
        "status_color",
        "updated_at_api"
    ))
    return JsonResponse(data, safe=False)
