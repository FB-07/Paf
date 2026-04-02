from django.shortcuts import render

from .. forms import FeadbackFrom

def mainpage(request):
    return render(request, "Mainpage.html")

def sobre(request):
    return render(request, "Sobre.html")

def doacoes(request):
    return render(request, "Doa.html")

def precaucoes(request):
    return render(request, "Preca.html")

def tabela(request):
    return render(request, "tabela.html")

def info(request):
    form = FeadbackFrom(request.POST or None)

    return render(request, "informacao.html", {"form": form})