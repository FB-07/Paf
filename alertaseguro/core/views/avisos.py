from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, time, timedelta
from ..models import Aviso

def avisos(request):
    agora = timezone.now()

    hoje_inicio = datetime.combine(agora.date(), time.min, tzinfo=timezone.get_current_timezone())

    limite_futuro = hoje_inicio + timedelta(days=3)

    avisos_qs = Aviso.objects.filter(
        Q(dataInicio__lte=limite_futuro) & Q(dataFim__gte=hoje_inicio)
    ).exclude(gravidade="green").order_by("gravidade", "dataInicio")

    return render(request, "Avisos.html", {"avisos": avisos_qs})