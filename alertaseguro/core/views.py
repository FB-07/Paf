import os
import json
import requests
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Incidente, UsersProfile, Aviso
from django.contrib.auth import authenticate, login, logout
from .forms import RegistoForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone


#############################
#                           #
#       Codigo inicio       #
#                           #
#############################

def mainpage(request):
    return render(request, "Mainpage.html")

def sobre(request):
    return render(request, "Sobre.html")

def doacoes(request):
    return render(request, "Doa.html")

def precaucoes(request):
    return render(request, "Preca.html")

#Avisos
def avisos(request):
    agora = timezone.now()
    avisos = Aviso.objects.filter(
        dataInicio__lte=agora,
        dataFim__gte=agora
    ).exclude(gravidade="green").order_by("gravidade", "dataInicio")
    print("DEBUG AVISOS:", avisos.count())
    return render(request, "Avisos.html", {"avisos": avisos})

#Incidentes
def incidentes_json(request):
    dados = list(Incidente.objects.values())
    return JsonResponse(dados, safe=False)

#Municipios incendio
@cache_page(60 * 60)
def rcm_hoje(request):
    r = requests.get(
        "https://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d0.json",
        timeout=10
    )
    r.raise_for_status()
    data = r.json()

    rcm0_dict = {
        str(dico).zfill(4): info["data"]["rcm"]
        for dico, info in data["local"].items()
    }
    return JsonResponse(rcm0_dict)

@cache_page(60 * 60)
def rcm_amanha(request):
    r = requests.get(
        "https://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d1.json",
        timeout=10
    )
    r.raise_for_status()
    data = r.json()

    rcm1_dict = {
        str(dico).zfill(4): info["data"]["rcm"]
        for dico, info in data["local"].items()
    }
    return JsonResponse(rcm1_dict)

#Prefil
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('mainpage')
        return render(request, "login.html", {"erro": "Credenciais inválidas"})

    return render(request, "login.html")


def registo_view(request):
    if request.method == "POST":
        form = RegistoForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
        return render(request, "registo.html", {"form": form})

    form = RegistoForm()
    return render(request, "registo.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('mainpage')

@login_required
def perfil_view(request):
    profile = UsersProfile.objects.get(user=request.user)
    return render(request, "perfil.html", {"profile": profile})
