from django.contrib import admin
from .models import (
    UsersProfile,
    IncidenteAPI,
    Hospital,
    Bombeiro,
    AirResource,
    Aviso,
    Notificacao,
    Weather,
    Feedback,
)

admin.site.register(UsersProfile)
admin.site.register(IncidenteAPI)
admin.site.register(Hospital)
admin.site.register(Bombeiro)
admin.site.register(AirResource)
admin.site.register(Aviso)
admin.site.register(Notificacao)
admin.site.register(Weather)
admin.site.register(Feedback)