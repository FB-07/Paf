from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ..forms import RegistoForm
from ..models import UsersProfile

def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            return redirect("mainpage")
        return render(request, "login.html", {"erro": "Credenciais inválidas"})
    return render(request, "login.html")

def registo_view(request):
    if request.method == "POST":
        form = RegistoForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect("login")
        return render(request, "registo.html", {"form": form})
    return render(request, "registo.html", {"form": RegistoForm()})

def logout_view(request):
    logout(request)
    return redirect("mainpage")

@login_required
def perfil_view(request):
    profile = UsersProfile.objects.get(user=request.user)
    return render(request, "perfil.html", {"profile": profile})
