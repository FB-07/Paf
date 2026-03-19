from django.contrib import admin
from .models import (
    UsersProfile,
    IncidenteAPI,
    NearbyFireStation,
    NearbyEmergency,
    NearbyAirbase,
    Aviso,
    Notificacao,
    Weather,
)

admin.site.register(UsersProfile)
admin.site.register(IncidenteAPI)
admin.site.register(NearbyFireStation)
admin.site.register(NearbyEmergency)
admin.site.register(NearbyAirbase)
admin.site.register(Aviso)
admin.site.register(Notificacao)
admin.site.register(Weather)