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
    AirResource
)

INCIDENTS_API = "https://ocorrenciasativas.pt/api/ocorrencias/incidents"
DETAIL_API = "https://api-dev.brlab.pt/v1/incidents/{}"

HOSPITAIS_API = "https://ocorrenciasativas.pt/api/hospitals"
BOMBEIROS_API = "https://ocorrenciasativas.pt/api/departments?page=1&limit=1000000000000"
AIR_API = "https://ocorrenciasativas.pt/api/air-resources?limit=1000000000000"

MAX_THREADS = 15

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

def fetch_incident_detail(id_oc):

    url = DETAIL_API.format(id_oc)

    data = fetch_json(url)

    if not data:
        return None

    items = data.get("data", [])

    if not items:
        return None

    return items[0]

def save_incident(item):

    id_oc = item.get("id_oc")

    incidente, _ = IncidenteAPI.objects.update_or_create(
        api_id=id_oc,
        defaults={

            "dico": item.get("dico"),

            "created_at_api": parse_datetime(
                item.get("dates", {}).get("started")
            ),

            "updated_at_api": parse_datetime(
                item.get("dates", {}).get("last_updated")
            ),

            "means_aerial": item.get("means_involved", {}).get("aerial", 0),
            "means_aquatic": item.get("means_involved", {}).get("aquatic", 0),
            "means_man": item.get("means_involved", {}).get("man", 0),
            "means_terrain": item.get("means_involved", {}).get("terrain", 0),

            "district": item.get("location", {}).get("district"),
            "county": item.get("location", {}).get("county"),
            "parish": item.get("location", {}).get("parish"),

            "location_name": item.get("location", {}).get("locality"),

            "region": item.get("location", {}).get("region"),
            "subregion": item.get("location", {}).get("subregion"),

            "latitude": item.get("coordinates", {}).get("latitude"),
            "longitude": item.get("coordinates", {}).get("longitude"),

            "status": item.get("occurrence", {}).get("status"),
            "status_color": item.get("occurrence", {}).get("statuscolor"),

            "natureza_code": item.get("occurrence", {}).get("naturezaCode"),
            "natureza": item.get("occurrence", {}).get("natureza"),
            "category": item.get("occurrence", {}).get("category"),

            "kml": item.get("occurrence", {}).get("kml"),

            "significant": item.get("occurrence", {}).get("significant", False),

            "raw": item,
        },
    )

    NearbyFireStation.objects.filter(incidente=incidente).delete()
    NearbyEmergency.objects.filter(incidente=incidente).delete()
    NearbyAirbase.objects.filter(incidente=incidente).delete()

    for fs in item.get("nearby_fire_station", []):
        NearbyFireStation.objects.create(
            incidente=incidente,
            name=fs.get("name"),
            latitude=fs.get("latitude"),
            longitude=fs.get("longitude"),
            distance=fs.get("distance"),
            logo=fs.get("logo"),
        )

    for em in item.get("nearby_emergencies", []):
        NearbyEmergency.objects.create(
            incidente=incidente,
            name=em.get("name"),
            latitude=em.get("latitude"),
            longitude=em.get("longitude"),
            distance=em.get("distance"),
        )

    for ab in item.get("nearby_airbases", []):
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

    existing = {
        i.api_id: i
        for i in IncidenteAPI.objects.all()
    }

    to_update = []
    active_ids = set()

    for item in incidents:

        id_oc = item.get("id_oc")
        active_ids.add(id_oc)

        last_updated_api = parse_datetime(
            item.get("dates", {}).get("last_updated")
        )

        db_incident = existing.get(id_oc)

        if not db_incident:
            to_update.append(id_oc)
            continue

        if last_updated_api and db_incident.updated_at_api != last_updated_api:
            to_update.append(id_oc)

    print(f"{len(to_update)} incidentes precisam de atualização")

    futures = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:

        for id_oc in to_update:

            futures.append(
                executor.submit(fetch_incident_detail, id_oc)
            )

        for future in as_completed(futures):

            detail = future.result()

            if not detail:
                continue

            save_incident(detail)

    closed = IncidenteAPI.objects.exclude(api_id__in=active_ids).update(
        status="Encerrada"
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
