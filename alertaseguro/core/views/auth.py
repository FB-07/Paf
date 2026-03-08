from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ..forms import RegistoForm
from ..models import UsersProfile
from django.contrib.auth.models import User

def login_view(request):
    if request.method == "POST":
        identifier = request.POST.get("username") 
        password = request.POST.get("password")

        user = authenticate(request, username=identifier, password=password)

        if not user:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            return redirect("mainpage")
        else:
            return render(request, "auth/login.html", {"erro": "Credenciais inválidas"})

    return render(request, "auth/login.html")

def registo_view(request):
    if request.method == "POST":
        form = RegistoForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect("login")
        return render(request, "auth/registo.html", {"form": form})
    return render(request, "auth/registo.html", {"form": RegistoForm()})

def logout_view(request):
    logout(request)
    return redirect("mainpage")

@login_required
def perfil_view(request):
    profile, created = UsersProfile.objects.get_or_create(user=request.user)
    return render(request, "auth/perfil.html", {"profile": profile})

@login_required
def editar_perfil(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = request.user

        if email:
            user.email = email
        if password:
            user.set_password(password)

        user.save()

        return redirect("perfil")

    return render(request, "auth/editar_perfil.html")