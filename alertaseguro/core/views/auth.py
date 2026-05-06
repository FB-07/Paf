from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.http import HttpResponse

from core.gmail_service import send_gmail_api

from django.template.loader import render_to_string
from django.utils.html import strip_tags

from ..forms import RegistoForm, LoginForm, EditarPerfilForm


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        identifier = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = None

        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            pass

        if user is None:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                user = None

        if user is None:
            messages.error(request, "Credenciais inválidas")
            return redirect("login")

        if not user.check_password(password):
            messages.error(request, "Credenciais inválidas")
            return redirect("login")

        if not user.is_active:
            messages.error(request, "Tens de verificar o teu email antes de fazer login")
            return redirect("login")

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        messages.success(request, "Login bem sucedido!")
        return redirect("mainpage")

    return render(request, "auth/login.html", {"form": form})


def registo_view(request):
    form = RegistoForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        link = request.build_absolute_uri(
            reverse(
                "verify_email",
                kwargs={
                    "uidb64": uid,
                    "token": token
                }
            )
        )

        delete_token = default_token_generator.make_token(user)

        delete_link = request.build_absolute_uri(
            reverse(
                "delete_account",
                kwargs={
                    "uidb64": uid,
                    "token": delete_token
                }
            )
        )

        domain = request.build_absolute_uri("/")[:-1]

        html_content = render_to_string(
            "emails/verify_email.html",
            {
                "user": user,
                "link": link,
                "delete_link": delete_link,
                "domain": domain,
            }
        )

        text_content = strip_tags(html_content)

        try:
            send_gmail_api(
                user.email,
                "AlertaSeguro: Verifica o teu email",
                text_content
            )

            messages.success(
                request,
                "Conta criada! Verifica o teu email."
            )

        except Exception as e:
            print(e)

            messages.error(
                request,
                "Erro ao enviar email."
            )

        return redirect("login")

    return render(request,"auth/registo.html",{"form": form})

def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse("Email verificado com sucesso!")

    return HttpResponse("Link inválido ou expirado.")

def delete_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.delete()
        messages.success(request, "Conta apagada com sucesso.")
    else:
        messages.error(request, "Link inválido.")

    return redirect("login")

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