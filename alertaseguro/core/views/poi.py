from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import Hospital, AirResource, Bombero
from django.core.paginator import Paginator

def bases_aereas(request):
    query = request.GET.get("q")

    air_resources = AirResource.objects.all()

    if query:
        air_resources = air_resources.filter(name__icontains=query)

    air_resources = air_resources.order_by("district", "name")

    paginator = Paginator(air_resources, 12)
    page_number = request.GET.get("page")
    air_resources = paginator.get_page(page_number)

    return render(request, "bases-aereas.html", {
        "air_resources": air_resources,
        "query": query,
    })


def hospitais(request):
    query = request.GET.get("q")

    hospitals = Hospital.objects.all()

    if query:
        hospitals = hospitals.filter(name__icontains=query)

    hospitals = hospitals.order_by("district", "name")

    paginator = Paginator(hospitals, 12)
    page_number = request.GET.get("page")
    hospitals = paginator.get_page(page_number)

    return render(request, "hospitais.html", {
        "hospitals": hospitals,
        "query": query,
    })


def bombeiros(request):
    query = request.GET.get("q")

    bomberos = Bombero.objects.all()

    if query:
        bomberos = bomberos.filter(name__icontains=query)

    bomberos = bomberos.order_by("district", "city")

    paginator = Paginator(bomberos, 12)
    page_number = request.GET.get("page")
    bomberos = paginator.get_page(page_number)

    return render(request, "bombeiros.html", {
        "bomberos": bomberos,
        "query": query,
    })