from django.contrib import messages
from django.shortcuts import render, redirect
from .. forms import FeedbackForm
from core.models import IncidenteAPI

def mainpage(request):
    return render(request, "Mainpage.html")

def sobre(request):
    return render(request, "Sobre.html")

def doacoes(request):
    return render(request, "Doa.html")

def precaucoes(request):
    return render(request, "Preca.html")

def info(request):
    return render(request, "informacao.html")

def tabela(request):
    return render(request, "tabela.html")

def feedback(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(f'/login/?next={request.path}')
        
        form = FeedbackForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, "Feedback enviado com sucesso!")
            return redirect('feedback')
        else:
            messages.error(request, "Preenche todos os campos obrigatórios.")
    else:
        form = FeedbackForm()

    return render(request, "feedback.html", {"form": form})