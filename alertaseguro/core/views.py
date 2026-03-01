import os
import json
import requests
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import IncidenteAPI, UsersProfile, Aviso
from django.contrib.auth import authenticate, login, logout
from .forms import RegistoForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone


#############################
#                           #
#       Codigo inicio       #
#                           #
#############################

ZONAS_IPMA = [
    {"sigla": "AVE", "nome": "Aveiro"},
    {"sigla": "BEJ", "nome": "Beja"},
    {"sigla": "BRA", "nome": "Braga"},
    {"sigla": "BRC", "nome": "Bragança"},
    {"sigla": "CAS", "nome": "Castelo Branco"},
    {"sigla": "COI", "nome": "Coimbra"},
    {"sigla": "EVO", "nome": "Évora"},
    {"sigla": "FAR", "nome": "Faro"},
    {"sigla": "GUA", "nome": "Guarda"},
    {"sigla": "LEI", "nome": "Leiria"},
    {"sigla": "LIS", "nome": "Lisboa"},
    {"sigla": "POR", "nome": "Porto"},
    {"sigla": "SAN", "nome": "Santarém"},
    {"sigla": "SET", "nome": "Setúbal"},
    {"sigla": "VIA", "nome": "Viana do Castelo"},
    {"sigla": "VIL", "nome": "Vila Real"},
    {"sigla": "VIS", "nome": "Viseu"},
    {"sigla": "MAD", "nome": "Madeira"},
    {"sigla": "ACO", "nome": "Açores"},
]
