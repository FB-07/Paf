from django.urls import include, path
from . import views

urlpatterns = [
    #Paginas
    path("", views.mainpage, name="mainpage"),
    path("sobre/", views.sobre, name="sobre"),
    path("doacoes/", views.doacoes, name="doacoes"),
    path("precaucoes/", views.precaucoes, name="precaucoes"),
    path("tabela/", views.tabela, name="tabela"),
    path("informacao/", views.info, name="informacao"),
    path("feedback/", views.feedback, name="feedback"),
    path("bases-aereas/", views.bases_aereas, name="bases_aereas"),
    path("hospitais/", views.hospitais, name="hospitais"),
    path("bombeiros/", views.bombeiros, name="bombeiros"),

    #Paginas de admin
    path("reports/", views.admin_reports, name="admin_reports"),

    #Login/Logout/Registo/Perfil
    path("login/", views.login_view, name="login"),
    path("registo/", views.registo_view, name="registo"),
    path("logout/", views.logout_view, name="logout"),
    path("perfil/", views.perfil_view, name="perfil"),
    path("editar-perfil/", views.editar_perfil, name="editar_perfil"),

    path('accounts/', include('allauth.urls')),

    #API
    path("avisos/", views.avisos, name="avisos"),

    path("api/incidentes/", views.api_incidentes, name="api_incidentes"),
    path("api/rcm/hoje/", views.rcm_hoje, name="rcm_hoje"),
    path("api/rcm/amanha/", views.rcm_amanha, name="rcm_amanha"),

    #Cron
    path("cron-import/", views.cron_import),
]

