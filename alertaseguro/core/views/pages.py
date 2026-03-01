from django.shortcuts import render

def mainpage(request):
    return render(request, "Mainpage.html")

def sobre(request):
    return render(request, "Sobre.html")

def doacoes(request):
    return render(request, "Doa.html")

def precaucoes(request):
    return render(request, "Preca.html")
