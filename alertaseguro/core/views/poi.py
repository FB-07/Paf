from django.shortcuts import render
from django.core.paginator import Paginator
from ..models import Hospital, AirResource, Bombeiro


def bombeiros(request):
    query = request.GET.get("q", "").strip()

    qs = Bombeiro.objects.all()

    if query:
        qs = qs.filter(name__icontains=query)

    qs = qs.order_by("district", "city")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "partials/bombeiros_results.html", {
            "bombeiros": qs
        })

    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    bombeiros = paginator.get_page(page_number)

    return render(request, "bombeiros.html", {
        "bombeiros": bombeiros,
        "query": query,
    })


def hospitais(request):
    query = request.GET.get("q", "").strip()

    qs = Hospital.objects.all()

    if query:
        qs = qs.filter(name__icontains=query)

    qs = qs.order_by("district", "name")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "partials/hospitais_results.html", {
            "hospitals": qs
        })

    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    hospitals = paginator.get_page(page_number)

    return render(request, "hospitais.html", {
        "hospitals": hospitals,
        "query": query,
    })


def bases_aereas(request):
    query = request.GET.get("q", "").strip()

    qs = AirResource.objects.all()

    if query:
        qs = qs.filter(name__icontains=query)

    qs = qs.order_by("district", "name")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "partials/bases_results.html", {
            "air_resources": qs
        })

    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    air_resources = paginator.get_page(page_number)

    return render(request, "bases-aereas.html", {
        "air_resources": air_resources,
        "query": query,
    })