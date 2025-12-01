from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Incidente, UsersProfile
from django.contrib.auth import authenticate, login, logout
from .forms import RegistoForm
from django.contrib.auth.decorators import login_required


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

def incidentes_json(request):
    dados = list(Incidente.objects.values())
    return JsonResponse(dados, safe=False)

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
