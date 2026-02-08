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
    path('login_view/', views.login_view, name='login'),
    path('registo_view/', views.registo_view, name='registo'),
    path('logout_view/', views.logout_view, name='logout'),
    path('perfil_view/', views.perfil_view, name='perfil'),


    #API
    path("api/incidentes/", views.incidentes_json, name="api_incidentes"),
    path("api/rcm_hoje/", views.rcm_hoje, name="rcm_hoje"),
    path("api/rcm_amanha/", views.rcm_hoje, name="rcm_amanha"),
]

