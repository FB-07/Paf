from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def bases_aerias(request):
    return render(request, "bases-aerias.html")

def hospitais(request):
    return render(request, "hospitais.html")

def bombeiros(request):
    return render(request, "bombeiros.html")