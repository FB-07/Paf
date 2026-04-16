from pyexpat.errors import messages
from django.shortcuts import render, redirect
from .. forms import FeedbackForm
from django.contrib.auth.decorators import login_required

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
    return render(request, "informacao.html")

def feedback(request):
    form = FeedbackForm()
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
                
    return render(request, "feedback.html", {"form": form})