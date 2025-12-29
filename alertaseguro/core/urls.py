from django.urls import path
from . import views

urlpatterns = [
    #Paginas
    path('', views.mainpage, name='mainpage'),
    path('sobre/', views.sobre, name='sobre'),
    path('doacoes/', views.doacoes, name='doacoes'),
    path('precaucoes/', views.precaucoes, name='precaucoes'),
    path('avisos/', views.avisos, name='avisos'),
    
    #Login/Logout/Registo/Perfil
    path('login/', views.login, name='login'),
    path('registo/', views.registo, name='registo'),
    path('logout/', views.logout, name='logout'),
    path('perfil/', views.perfil, name='perfil'),


    #API
    path("api/incidentes/", views.incidentes_json, name="api_incidentes"),
    path("api/rcm_hoje/", views.rcm_hoje, name="rcm_hoje"),
]

