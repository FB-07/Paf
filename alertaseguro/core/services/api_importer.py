import requests
from datetime import datetime
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.models import (
    IncidenteAPI,
    Hospital,
    Bombeiro,
    AirResource,
    Weather,
)

INCIDENTS_API = "https://ocorrenciasativas.pt/api/ocorrencias/incidents"
DETAIL_API = "https://api-dev.brlab.pt/v1/incidents/{}"

HOSPITAIS_API = "https://ocorrenciasativas.pt/api/hospitals"
BOMBEIROS_API = "https://ocorrenciasativas.pt/api/departments?page=1&limit=1000000000000"
AIR_API = "https://ocorrenciasativas.pt/api/air-resources?limit=1000000000000"

MAX_THREADS = 15

# =========================
# SESSION (FIX SSL + POOL)
# =========================
session = requests.Session()

retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(
    max_retries=retries,
    pool_connections=30,
    pool_maxsize=30
)

session.mount("https://", adapter)
session.mount("http://", adapter)


def fetch_json(url):
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[API ERROR] {url}: {e}")
        return None


def parse_datetime(value):
    if not value:
        return None

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%d-%m-%Y %H:%M",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            return dt
        except:
            continue

    return None


def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0


# =========================
# DETAIL FETCH
# =========================
def fetch_incident_detail(incident_id):
    data = fetch_json(DETAIL_API.format(incident_id))
    if not data:
        return None
    items = data.get("data", [])
    return items[0] if items else None


# =========================
# DB SAVE (THREAD SAFE)
# =========================
def save_incident(item):
    if not item:
        return

    api_id = item.get("id")
    if not api_id:
        return

    location = item.get("location") or {}
    means = item.get("means_involved") or {}
    coords = item.get("coordinates") or {}
    occ = item.get("occurrence") or {}

    incidente, _ = IncidenteAPI.objects.update_or_create(
        api_id=api_id,
        defaults={
            "dico": item.get("dico"),
            "created_at_api": parse_datetime(item.get("dates", {}).get("started")),
            "updated_at_api": parse_datetime(item.get("dates", {}).get("last_updated")),

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
            "significant": occ.get("significant", False),

            "nearby_data": {
                "fire_stations": item.get("nearby_fire_station", []),
                "hospitals": item.get("nearby_emergencies", []),
                "airbases": item.get("nearby_airbases", []),
            },

            "raw": item,
        }
    )

    weather = item.get("weather") or {}
    if isinstance(weather, dict):
        wind = weather.get("wind_direction") or {}

        Weather.objects.update_or_create(
            incidente=incidente,
            defaults={
                "station": weather.get("station"),
                "distance_km": safe_float(weather.get("distance_km")),
                "temperature_c": weather.get("temperature_c"),
                "humidity_percent": weather.get("humidity_percent"),
                "wind_kmh": weather.get("wind_kmh"),
                "precipitation_mmh": weather.get("precipitation_mmh"),
                "pressure_hpa": weather.get("pressure_hpa"),
                "description": weather.get("description"),
                "wind_degree": wind.get("degree"),
                "wind_cardinal": wind.get("cardinal"),
            }
        )


# =========================
# INCIDENT IMPORT (FIX LOCK)
# =========================
def import_incidents():
    data = fetch_json(INCIDENTS_API)

    if data is None:
        print("API falhou")
        return

    incidents = data.get("data", [])
    existing = {i.api_id: i for i in IncidenteAPI.objects.all()}
    active_ids = set()

    to_fetch = []

    for item in incidents:
        api_id = item.get("id")
        if not api_id:
            continue

        active_ids.add(api_id)

        last_updated = parse_datetime(item.get("dates", {}).get("last_updated"))
        db_item = existing.get(api_id)

        if not db_item or (last_updated and db_item.updated_at_api != last_updated):
            to_fetch.append(api_id)

    # =========================
    # THREADS APENAS PARA API CALLS
    # =========================
    results = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(fetch_incident_detail, i) for i in to_fetch]

        for future in as_completed(futures):
            detail = future.result()
            if detail:
                results.append(detail)

    # =========================
    # DB WRITE SERIALIZADO (FIX SQLITE LOCK)
    # =========================
    for item in results:
        save_incident(item)

    IncidenteAPI.objects.exclude(api_id__in=active_ids).exclude(status="Encerrada").update(
        status="Encerrada",
        status_color="#4d4d4d",
        updated_at_api=timezone.now()
    )


# =========================
# RESTO (igual, seguro)
# =========================
def import_hospitals():
    data = fetch_json(HOSPITAIS_API)
    if not data:
        return

    for item in data.get("data", []):
        Hospital.objects.update_or_create(
            api_id=item.get("id"),
            defaults=item
        )


def import_bombeiros():
    data = fetch_json(BOMBEIROS_API)
    if not data:
        return

    for item in data.get("data", []):
        Bombeiro.objects.update_or_create(
            api_id=item.get("id"),
            defaults=item
        )


def import_air_resources():
    data = fetch_json(AIR_API)
    if not data:
        return

    for item in data.get("data", []):
        AirResource.objects.update_or_create(
            api_id=item.get("id"),
            defaults=item
        )


def fetch_all_apis():
    import_incidents()


def locais():
    import_hospitals()
    import_bombeiros()
    import_air_resources()