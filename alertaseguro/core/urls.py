from django.urls import path
from . import views

urlpatterns = [
    path('', views.mainpage, name='mainpage'),
    path('sobre/', views.sobre, name='sobre'),
    path('doacoes/', views.doacoes, name='doacoes'),
    path('precaucoes/', views.precaucoes, name='precaucoes'),
    
    #Login/Logout/Registo/Perfil
    path('login/', views.login_view, name='login'),
    path('registo/', views.registo_view, name='registo'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),


    #API
    path("api/incidentes/", views.incidentes_json, name="api_incidentes"),
]

