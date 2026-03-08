# core/services/api_importer.py

import requests
from datetime import datetime
from django.utils import timezone
from core.models import IncidenteAPI, NearbyFireStation, NearbyEmergency, NearbyAirbase
from core.models import Hospital, Bombero, AirResource

def parse_datetime(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except:
            continue
    return None

def fetch_all_apis():
    print("🧹 Limpando dados antigos...")

    IncidenteAPI.objects.all().delete()
    NearbyFireStation.objects.all().delete()
    NearbyEmergency.objects.all().delete()
    NearbyAirbase.objects.all().delete()
    Hospital.objects.all().delete()
    Bombero.objects.all().delete()
    AirResource.objects.all().delete()

    print("✅ Base limpa. Importando dados novos...")
    # -------------------
    # API INCIDENTES
    # -------------------
    INCIDENTS_API = "https://ocorrenciasativas.pt/api/ocorrencias/incidents"
    try:
        r = requests.get(INCIDENTS_API, timeout=30)
        r.raise_for_status()
        payload = r.json()
        incidentes = payload.get("data", [])
        for item in incidentes:
            incidente, _ = IncidenteAPI.objects.update_or_create(
                api_id=item.get("id_oc"),
                defaults={
                    "dico": item.get("dico"),
                    "created_at_api": parse_datetime(item.get("date", {}).get("created")),
                    "updated_at_api": parse_datetime(item.get("date", {}).get("updated")),
                    "means_aerial": item.get("means_involved", {}).get("aerial", 0),
                    "means_aquatic": item.get("means_involved", {}).get("aquatic", 0),
                    "means_man": item.get("means_involved", {}).get("man", 0),
                    "means_terrain": item.get("means_involved", {}).get("terrain", 0),
                    "district": item.get("location", {}).get("district"),
                    "county": item.get("location", {}).get("county"),
                    "parish": item.get("location", {}).get("parish"),
                    "location_name": item.get("location", {}).get("location"),
                    "region": item.get("location", {}).get("region"),
                    "subregion": item.get("location", {}).get("subregion"),
                    "coords_ok": item.get("coordinates", {}).get("coords", False),
                    "latitude": item.get("coordinates", {}).get("latitude"),
                    "longitude": item.get("coordinates", {}).get("longitude"),
                    "is_fire": item.get("occurrence", {}).get("fire", False),
                    "is_accident": item.get("occurrence", {}).get("accident", False),
                    "is_meteo": item.get("occurrence", {}).get("meteo", False),
                    "status_code": item.get("occurrence", {}).get("statusCode"),
                    "status_color": item.get("occurrence", {}).get("statuscolor"),
                    "status": item.get("occurrence", {}).get("status"),
                    "natureza_code": item.get("occurrence", {}).get("naturezaCode"),
                    "natureza": item.get("occurrence", {}).get("natureza"),
                    "category": item.get("occurrence", {}).get("category"),
                    "kml": item.get("occurrence", {}).get("kml"),
                    "significant": item.get("occurrence", {}).get("significant", False),
                    "active": item.get("active", True),
                    "icnf_altitude": item.get("icnf", {}).get("altitude", 0),
                    "icnf_fogacho": item.get("icnf", {}).get("fogacho", False),
                    "icnf_fonte_alerta": item.get("icnf", {}).get("fontealerta"),
                    "burned_area": item.get("burned", {}).get("burned_area"),
                    "burned_area_agricultural": item.get("burned", {}).get("burned_area_agricultural"),
                    "burned_area_bush": item.get("burned", {}).get("burned_area_bush"),
                    "burned_area_forest": item.get("burned", {}).get("burned_area_forest"),
                    "fire_duration": item.get("burned", {}).get("fire_duration", 0),
                    "burned_area_created_at": item.get("burned", {}).get("burned_area_created_at"),
                    "burned_area_updated_at": item.get("burned", {}).get("burned_area_updated_at"),
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
        print(f"API INCIDENTES atualizada ({len(incidentes)} registros).")
    except Exception as e:
        print(f"Erro API INCIDENTES: {e}")

    # -------------------
    # API HOSPITAIS
    # -------------------
    HOSPITAIS_API = "https://ocorrenciasativas.pt/api/hospitals"
    try:
        r = requests.get(HOSPITAIS_API, timeout=30)
        r.raise_for_status()
        hospitais = r.json().get("data", [])

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

        print(f"API HOSPITAIS atualizada ({len(hospitais)} registros).")
    except Exception as e:
        print(f"Erro API HOSPITAIS: {e}")


    # -------------------
    # API BOMBEIROS
    # -------------------
    BOMBEIROS_API = "https://ocorrenciasativas.pt/api/departments?page=1&limit=1000000000000"
    try:
        r = requests.get(BOMBEIROS_API, timeout=30)
        r.raise_for_status()
        bombeiros = r.json().get("data", [])

        for item in bombeiros:
            Bombero.objects.update_or_create(
                api_id=item.get("id"),
                defaults={
                    "name": item.get("name"),
                    "latitude": item.get("latitude"),
                    "longitude": item.get("longitude"),
                    "district": item.get("district"),
                    "county": item.get("county"),
                    "raw": item,
                },
            )

        print(f"API BOMBEIROS atualizada ({len(bombeiros)} registros).")
    except Exception as e:
        print(f"Erro API BOMBEIROS: {e}")


    # -------------------
    # API RECURSOS AÉREOS
    # -------------------
    AIR_API = "https://ocorrenciasativas.pt/api/air-resources?limit=1000000000000"
    try:
        r = requests.get(AIR_API, timeout=30)
        r.raise_for_status()
        recursos = r.json().get("data", [])

        for item in recursos:
            AirResource.objects.update_or_create(
                api_id=item.get("id"),
                defaults={
                    "name": item.get("name"),
                    "latitude": item.get("latitude"),
                    "longitude": item.get("longitude"),
                    "status": item.get("status"),
                    "type": item.get("type"),
                    "raw": item,
                },
            )

        print(f"API RECURSOS AÉREOS atualizada ({len(recursos)} registros).")
    except Exception as e:
        print(f"Erro API RECURSOS AÉREOS: {e}")

# =========================
# Função compatível com scheduler
# =========================
def fetch_and_save():
    fetch_all_apis()