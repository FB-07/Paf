import requests
from datetime import datetime
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.models import (
    IncidenteAPI,
    NearbyFireStation,
    NearbyEmergency,
    NearbyAirbase,
    Hospital,
    Bombero,
    AirResource,
    Weather,
)

INCIDENTS_API = "https://ocorrenciasativas.pt/api/ocorrencias/incidents"
DETAIL_API = "https://api-dev.brlab.pt/v1/incidents/{}"

HOSPITAIS_API = "https://ocorrenciasativas.pt/api/hospitals"
BOMBEIROS_API = "https://ocorrenciasativas.pt/api/departments?page=1&limit=1000000000000"
AIR_API = "https://ocorrenciasativas.pt/api/air-resources?limit=1000000000000"

MAX_THREADS = 15


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


def parse_datetime(value):
    if not value:
        return None

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%Y-%m-%dT%H:%M:%S",
    ):
        try:
            dt = datetime.strptime(value, fmt)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            return dt
        except:
            continue

    return None


def fetch_json(url):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Erro request {url}: {e}")
        return None


def fetch_incident_detail(id):
    url = DETAIL_API.format(id)
    data = fetch_json(url)

    if not data:
        return None

    items = data.get("data", [])
    if not items:
        return None

    return items[0]


def save_incident(item):

    if not item:
        return

    id = item.get("id")

    if not id:
        return

    location = item.get("location") or {}
    means = item.get("means_involved") or {}
    coords = item.get("coordinates") or {}
    occ = item.get("occurrence") or {}

    incidente, _ = IncidenteAPI.objects.update_or_create(
        api_id=id,
        defaults={
            "dico": item.get("dico"),

            "created_at_api": parse_datetime(
                item.get("dates", {}).get("started")
            ),
            "updated_at_api": parse_datetime(
                item.get("dates", {}).get("last_updated")
            ),

            "means_aerial": means.get("aerial", 0),
            "means_aquatic": means.get("aquatic", 0),
            "means_man": means.get("man", 0),
            "means_terrain": means.get("terrain", 0),

            "district": location.get("district"),
            "county": location.get("county"),
            "parish": location.get("parish"),
            "location_name": location.get("locality"),
            "region": location.get("region"),
            "subregion": location.get("subregion"),

            "latitude": coords.get("latitude"),
            "longitude": coords.get("longitude"),

            "status": occ.get("status"),
            "status_color": occ.get("statuscolor"),
            "natureza_code": occ.get("naturezaCode"),
            "natureza": occ.get("natureza"),
            "category": occ.get("category"),
            "kml": occ.get("kml"),
            "significant": occ.get("significant", False),

            "raw": item,
        },
    )

    weather = item.get("weather") or {}

    if isinstance(weather, dict):

        wind_direction = weather.get("wind_direction") or {}

        if not isinstance(wind_direction, dict):
            wind_direction = {}

        Weather.objects.update_or_create(
            incidente=incidente,
            defaults={
                "station": weather.get("station"),
                "distance_km": safe_float(weather.get("distance_km")),

                "temperature_c": safe_float(weather.get("temperature_c")),
                "temperature_min_c": safe_float(weather.get("temperature_min_c")),
                "temperature_max_c": safe_float(weather.get("temperature_max_c")),

                "humidity_percent": weather.get("humidity_percent"),
                "wind_kmh": safe_float(weather.get("wind_kmh")),
                "precipitation_mmh": safe_float(weather.get("precipitation_mmh")),
                "pressure_hpa": weather.get("pressure_hpa"),

                "description": weather.get("description"),

                "wind_degree": wind_direction.get("degree"),
                "wind_cardinal": wind_direction.get("cardinal"),
            },
        )

    NearbyFireStation.objects.filter(incidente=incidente).delete()
    NearbyEmergency.objects.filter(incidente=incidente).delete()
    NearbyAirbase.objects.filter(incidente=incidente).delete()

    for fs in item.get("nearby_fire_station", []) or []:
        NearbyFireStation.objects.create(
            incidente=incidente,
            name=fs.get("name"),
            latitude=fs.get("latitude"),
            longitude=fs.get("longitude"),
            distance=fs.get("distance"),
            logo=fs.get("logo"),
        )

    for em in item.get("nearby_emergencies", []) or []:
        NearbyEmergency.objects.create(
            incidente=incidente,
            name=em.get("name"),
            latitude=em.get("latitude"),
            longitude=em.get("longitude"),
            distance=em.get("distance"),
        )

    for ab in item.get("nearby_airbases", []) or []:
        NearbyAirbase.objects.create(
            incidente=incidente,
            name=ab.get("name"),
            latitude=ab.get("latitude"),
            longitude=ab.get("longitude"),
            distance=ab.get("distance"),
        )


def import_incidents():

    print("Importando INCIDENTES...")

    data = fetch_json(INCIDENTS_API)

    if not data:
        return

    incidents = data.get("data", [])

    print(f"{len(incidents)} incidentes ativos na API")

    existing = {i.api_id: i for i in IncidenteAPI.objects.all()}

    to_update = []
    active_ids = set()

    for item in incidents:

        api_id = item.get("id")
        if not api_id:
            continue

        active_ids.add(api_id)

        last_updated_api = parse_datetime(
            item.get("dates", {}).get("last_updated")
        )

        db_incident = existing.get(api_id)

        if not db_incident:
            to_update.append(api_id)
            continue

        if last_updated_api and db_incident.updated_at_api != last_updated_api:
            to_update.append(api_id)

    print(f"{len(to_update)} incidentes precisam de atualização")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [
            executor.submit(fetch_incident_detail, i)
            for i in to_update
        ]

        for future in as_completed(futures):
            detail = future.result()
            if detail:
                save_incident(detail)

    closed_qs = IncidenteAPI.objects.exclude(
        api_id__in=active_ids
    ).exclude(status="Encerrada")

    closed = closed_qs.update(
        status="Encerrada",
        updated_at_api=timezone.now()
    )

    print(f"{closed} incidentes marcados como encerrados")

    print("Incidentes atualizados.")


def import_hospitals():

    print("Importando HOSPITAIS...")

    data = fetch_json(HOSPITAIS_API)

    if not data:
        return

    hospitais = data.get("data", [])

    for item in hospitais:

        Hospital.objects.update_or_create(
            api_id=item.get("id"),
            defaults={
                "name": item.get("name"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "address": item.get("address"),
                "phone": item.get("phone"),
                "raw": item,
            },
        )

    print(f"{len(hospitais)} hospitais importados")


def import_bombeiros():

    print("Importando BOMBEIROS...")

    data = fetch_json(BOMBEIROS_API)

    if not data:
        return

    bombeiros = data.get("data", [])

    for item in bombeiros:

        Bombero.objects.update_or_create(
            api_id=item.get("id"),
            defaults={
                "name": item.get("name"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "district": item.get("district"),
                "city": item.get("county"),
                "raw": item,
            },
        )

    print(f"{len(bombeiros)} bombeiros importados")


def import_air_resources():

    print("Importando RECURSOS AÉREOS...")

    data = fetch_json(AIR_API)

    if not data:
        return

    recursos = data.get("data", [])

    for item in recursos:

        AirResource.objects.update_or_create(
            api_id=item.get("id"),
            defaults={
                "name": item.get("name"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "type": item.get("type"),
                "raw": item,
            },
        )

    print(f"{len(recursos)} recursos importados")


def fetch_all_apis():

    print("Importando dados ...")

    import_incidents()
    import_hospitals()
    import_bombeiros()
    import_air_resources()

    print("IMPORT COMPLETO")


def fetch_all_apis_clean():

    print("🧹 Limpando dados antigos...")

    IncidenteAPI.objects.all().delete()
    NearbyFireStation.objects.all().delete()
    NearbyEmergency.objects.all().delete()
    NearbyAirbase.objects.all().delete()

    print("Base limpa")

    import_incidents()
    import_hospitals()
    import_bombeiros()
    import_air_resources()

    print("IMPORT COMPLETO")