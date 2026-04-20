from django.http import JsonResponse
from core.models import IncidenteAPI


def api_incidentes(request):

    incidentes = (
        IncidenteAPI.objects
        .filter(latitude__isnull=False, longitude__isnull=False)
        .exclude(status="Encerrada")
        .select_related("weather")
    )

    data = []

    for inc in incidentes:

        weather = getattr(inc, "weather", None)
        nearby = inc.nearby_data or {}

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

            "means": {
                "aerial": inc.means_aerial,
                "terrain": inc.means_terrain,
                "aquatic": inc.means_aquatic,
                "man": inc.means_man,
            },

            "kml": inc.kml or None,

            "weather": {
                "temperature_c": weather.temperature_c,
                "humidity_percent": weather.humidity_percent,
                "wind_kmh": weather.wind_kmh,
                "wind_cardinal": weather.wind_cardinal,
                "wind_degree": weather.wind_degree,
                "pressure_hpa": weather.pressure_hpa,
                "precipitation_mmh": weather.precipitation_mmh,
                "description": weather.description,
            } if weather else None,

            "nearby_fire_stations": nearby.get("fire_stations", []),
            "nearby_emergencies": nearby.get("hospitals", []),
            "nearby_airbases": nearby.get("airbases", []),
        })

    return JsonResponse(data, safe=False)