import requests
from django.http import JsonResponse
from django.views.decorators.cache import cache_page

@cache_page(60 * 60)
def rcm_hoje(request):
    r = requests.get(
        "https://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d0.json",
        timeout=10
    )
    r.raise_for_status()
    data = r.json()

    rcm0_dict = {
        str(dico).zfill(4): info["data"]["rcm"]
        for dico, info in data["local"].items()
    }
    return JsonResponse(rcm0_dict)

@cache_page(60 * 60)
def rcm_amanha(request):
    r = requests.get(
        "https://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d1.json",
        timeout=10
    )
    r.raise_for_status()
    data = r.json()

    rcm1_dict = {
        str(dico).zfill(4): info["data"]["rcm"]
        for dico, info in data["local"].items()
    }
    return JsonResponse(rcm1_dict)
