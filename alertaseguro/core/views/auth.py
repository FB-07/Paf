from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from ..forms import RegistoForm
from ..forms import LoginForm
from ..forms import EditarPerfilForm

def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.user)
        messages.success(request, "Login bem sucedido!")
        return redirect("mainpage")
    return render(request, "auth/login.html", {"form": form})

def registo_view(request):
    if request.method == "POST":
        form = RegistoForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Registo bem sucedido!")
            return redirect("login")
        return render(request, "auth/registo.html", {"form": form})
    return render(request, "auth/registo.html", {"form": RegistoForm()})

def logout_view(request):
    logout(request)
    messages.success(request, "Successfully signed out.")
    return redirect("mainpage")

@login_required
def perfil_view(request):
    return render(request, "auth/perfil.html")

@login_required
def editar_perfil(request):
    form = EditarPerfilForm(request.POST or None, instance=request.user)

    if request.method == "POST" and form.is_valid():
        user = form.save()

        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)

        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect("perfil")

    return render(request, "auth/editar_perfil.html", {"form": form})