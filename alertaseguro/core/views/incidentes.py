from django.http import JsonResponse
from core.models import IncidenteAPI

def api_incidentes(request):
    incidentes = IncidenteAPI.objects.filter(latitude__isnull=False, longitude__isnull=False).exclude(status="Encerrada")

    data = []
    for inc in incidentes:
        data.append({
            "api_id": inc.api_id,
            "latitude": float(inc.latitude),
            "longitude": float(inc.longitude),
            "natureza": inc.natureza or "",
            "category": inc.category or "",
            "location_name": inc.location_name or "",
            "parish": inc.parish or "",
            "county": inc.county or "",
            "district": inc.district or "",
            "status": inc.status or "",
            "status_color": inc.status_color or "#333",
            "updated_at_api": inc.updated_at_api.isoformat() if inc.updated_at_api else "",
            "means_aerial": inc.means_aerial or 0,
            "means_terrain": inc.means_terrain or 0,
            "means_aquatic": inc.means_aquatic or 0,
            "means_man": inc.means_man or 0,
            "kml": inc.kml or None,
        })

    return JsonResponse(data, safe=False)