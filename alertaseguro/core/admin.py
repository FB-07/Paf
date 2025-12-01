from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import (
    TipoIncidente,
    UsersProfile,
    Incidente,
    Aviso,
    Notificacao,
    HistoricoIncidentes
)

admin.site.register(TipoIncidente)
admin.site.register(UsersProfile)
admin.site.register(Incidente)
admin.site.register(Aviso)
admin.site.register(Notificacao)
admin.site.register(HistoricoIncidentes)
